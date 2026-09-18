"""Lyse single-shot routine: log shot metadata + analysis results to InfluxDB.

Writes one InfluxDB point per shot to the Telegraf listener that the
DatabaseDevelopment stack runs (monitoring/docker-compose.yml). Telegraf fans
the point out to the local InfluxDB *and* to Grafana Cloud, so nothing here
needs influxdb_client or any credentials -- the listener is plain HTTP line
protocol on localhost with no token auth.

Extending it: see the "What gets logged" block below. Adding a new result
group, global, or derived quantity is a one-line change; nothing downstream
needs to know about the new field.

Re-running this routine on a shot rewrites the same point (same measurement,
tag set and timestamp), so it is idempotent -- no duplicates in the database.
"""

import os
import datetime

import lyse
import h5py
import numpy as np
import requests


# ── Where it goes ─────────────────────────────────────────────────────────────
# Telegraf's influxdb_v2_listener on the monitoring server (docker-compose maps
# container :8087 to that host). It routes on the ?bucket= query param via
# bucket_tag, so the bucket below must exist in the server's InfluxDB.
#
# The listener takes no token -- it is unauthenticated on the lab network, so
# the host is set here rather than being discoverable, and LICS_TELEGRAF_URL
# overrides it (point it at localhost when testing against a local stack).
TELEGRAF_HOST = os.environ.get('LICS_TELEGRAF_HOST', '192.168.1.104')
TELEGRAF_URL = os.environ.get(
    'LICS_TELEGRAF_URL', f'http://{TELEGRAF_HOST}:8087/api/v2/write'
)
BUCKET = 'mainLab'
MEASUREMENT = 'shot'
TIMEOUT_S = 2.0


# ── What gets logged ──────────────────────────────────────────────────────────
# 1. Every attribute of results/<group> for each group named here. These are
#    what BLACS/lyse analysis routines write with save_result(), so the whole
#    group is picked up automatically as routines gain new outputs.
RESULT_GROUPS = ['live_image_analysis']
# e.g. RESULT_GROUPS = ['live_image_analysis', 'absorption_image_analysis']

# 2. Runmanager globals to log alongside the results, by name.
GLOBALS = []
# e.g. GLOBALS = ['Cs_MOT_load_time', 'TOF_time']

# 3. Anything that has to be computed. Each entry maps a field name to a
#    callable taking the open h5py.File and returning a scalar (or None to
#    skip). Exceptions are swallowed, so a broken entry cannot lose the shot.
EXTRA_FIELDS = {}
# e.g. EXTRA_FIELDS = {
#     'peak_od': lambda f: float(np.nanmax(f['images/pco_panda/absorption1/density'][:])),
# }

# Which metadata keys become InfluxDB *tags* rather than fields. Tags are
# indexed and become Prometheus labels in Grafana Cloud, so only low-cardinality
# things belong here: sequence_name is one of a handful of script names, while
# shot_path and sequence_id are unique per shot/sequence and would blow up
# series cardinality. Non-tag strings stay as fields -- InfluxDB stores them
# fine; Grafana Cloud's Prometheus remote-write silently drops them, which is
# the intended split.
TAG_KEYS = ('sequence_name',)


# ── Line protocol ─────────────────────────────────────────────────────────────

def _escape_key(value):
    """Escape a measurement/tag/field *key* or tag value for line protocol."""
    return (str(value).replace('\\', '\\\\').replace(',', '\\,')
                      .replace('=', '\\=').replace(' ', '\\ '))


def _format_value(value):
    """Render a Python value as a line-protocol field value, or None to skip."""
    if isinstance(value, bytes):
        value = value.decode('utf-8', 'replace')
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, (bool, np.bool_)):
        return 'true' if value else 'false'
    if isinstance(value, int):
        return f'{value}i'
    if isinstance(value, float):
        # NaN/inf are not representable in line protocol; a failed fit should
        # leave a gap in the series rather than reject the whole write.
        if not np.isfinite(value):
            return None
        return repr(value)
    if isinstance(value, str):
        escaped = value.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'
    return None  # arrays, None, anything else: not a scalar, do not log it


def build_line(measurement, tags, fields, timestamp_ns):
    """Assemble one InfluxDB line-protocol point."""
    rendered = {}
    for key, value in fields.items():
        formatted = _format_value(value)
        if formatted is not None:
            rendered[_escape_key(key)] = formatted
    if not rendered:
        raise ValueError('refusing to write a point with no fields')

    line = _escape_key(measurement)
    for key, value in sorted(tags.items()):
        if value is not None and value != '':
            line += f',{_escape_key(key)}={_escape_key(value)}'
    line += ' ' + ','.join(f'{k}={v}' for k, v in sorted(rendered.items()))
    return f'{line} {timestamp_ns}'


# ── Gathering the shot's data ─────────────────────────────────────────────────

def shot_relative_path(shot_path):
    """Path of the shot file relative to experiment_shot_storage.

    Falls back to the absolute path if the labconfig cannot be read or the shot
    lives outside the configured storage root.
    """
    try:
        from labscript_utils.labconfig import LabConfig
        storage = LabConfig().get('DEFAULT', 'experiment_shot_storage')
        relative = os.path.relpath(shot_path, storage)
        if relative.startswith(os.pardir):
            return shot_path.replace(os.sep, '/')
        return relative.replace(os.sep, '/')
    except Exception:
        return shot_path.replace(os.sep, '/')


def shot_timestamp_ns(h5_file):
    """Epoch nanoseconds of the shot itself, from the 'run time' root attribute.

    Timestamping with the shot's own time (rather than now) means a re-analysed
    or back-filled shot lands where it belongs on the Grafana time axis.
    """
    run_time = h5_file.attrs.get('run time')
    if isinstance(run_time, bytes):
        run_time = run_time.decode()
    if run_time:
        try:
            # e.g. '20260914T183156.335996', naive local time
            dt = datetime.datetime.strptime(str(run_time), '%Y%m%dT%H%M%S.%f')
            return int(dt.timestamp() * 1e9)
        except ValueError:
            pass
    return int(datetime.datetime.now().timestamp() * 1e9)


def collect(shot_path):
    """Return (tags, fields, timestamp_ns) for one shot."""
    metadata = {}
    fields = {}

    with h5py.File(shot_path, 'r') as f:
        attrs = f.attrs

        def text(key):
            value = attrs.get(key)
            if isinstance(value, bytes):
                value = value.decode()
            return None if value is None else str(value)

        def integer(key):
            return int(attrs[key]) if key in attrs else None

        # Sequence identity. sequence_index restarts each day, so sequence_id
        # (date-stamped) is what actually identifies a sequence uniquely.
        metadata['sequence_name'] = text('script_basename')
        metadata['sequence_id'] = text('sequence_id')
        metadata['sequence_index'] = integer('sequence_index')
        metadata['run_number'] = integer('run number')
        metadata['n_runs'] = integer('n_runs')
        metadata['shot_path'] = shot_relative_path(shot_path)

        # 1. Analysis result groups, whole-group.
        for group_name in RESULT_GROUPS:
            group = f.get(f'results/{group_name}')
            if group is None:
                continue
            for key, value in group.attrs.items():
                # Prefix only when logging more than one group, so the common
                # single-group case keeps short field names in Grafana.
                name = key if len(RESULT_GROUPS) == 1 else f'{group_name}.{key}'
                fields[name] = value

        # 2. Globals.
        globals_group = f.get('globals')
        if globals_group is not None:
            for name in GLOBALS:
                if name in globals_group.attrs:
                    fields[name] = globals_group.attrs[name]

        # 3. Computed extras.
        for name, getter in EXTRA_FIELDS.items():
            try:
                fields[name] = getter(f)
            except Exception as exc:
                print(f'influx_shot_logger: EXTRA_FIELDS[{name!r}] failed: {exc}')

        timestamp_ns = shot_timestamp_ns(f)

    tags = {k: v for k, v in metadata.items() if k in TAG_KEYS}
    fields.update({k: v for k, v in metadata.items() if k not in TAG_KEYS})
    return tags, fields, timestamp_ns


def log_shot(shot_path, url=TELEGRAF_URL, bucket=BUCKET):
    """Collect and write one shot. Returns True on success.

    Never raises: a database that is down (the docker stack not running, say)
    must not fail the shot's analysis in lyse.
    """
    try:
        tags, fields, timestamp_ns = collect(shot_path)
        line = build_line(MEASUREMENT, tags, fields, timestamp_ns)
    except Exception as exc:
        print(f'influx_shot_logger: could not build point: {exc}')
        return False

    try:
        response = requests.post(
            url, params={'bucket': bucket}, data=line.encode('utf-8'),
            timeout=TIMEOUT_S,
        )
        response.raise_for_status()
    except Exception as exc:
        print(f'influx_shot_logger: write to {url} failed ({exc}); point was:\n{line}')
        return False

    print(f'influx_shot_logger: logged {len(fields)} fields to bucket {bucket!r}')
    return True


if lyse.path is not None:
    log_shot(lyse.path)
