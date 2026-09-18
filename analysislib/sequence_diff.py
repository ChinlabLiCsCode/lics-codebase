"""Diff two labscript shots: globals, script source, and compiled hardware output.

"What changed between the run that worked and the run that doesn't" is three
questions, and a shot file answers all three:

* ``/globals``          -- the knobs, raw expressions and evaluated values
* ``/script``           -- the labscript source that was compiled
* ``/devices/...``      -- the instruction tables that actually reached the
                           hardware, which is the only layer that says whether
                           a globals change had any effect at all

The third one is the point of this module.  A globals diff after a refactor is
enormous and mostly noise; the channel diff is short and says which output on
which box moved, and when.  Channels are named and timestamped, so a row reads
``Cs_MOT_AO_AM  first delta @ t=3.161`` rather than ``NIBox3/AO row 4021``.

Usage, from a notebook::

    from analysislib.sequence_diff import diff_shots
    print(diff_shots('2026-09-15_0012_cs_molasses_healthcheck_59',
                     '2026-09-18_0003_cs_molasses_healthcheck_0'))

or from a shell::

    python -m analysislib.sequence_diff SHOT_A SHOT_B [--full-script] [--all-channels]

Either argument may be a full path or a bare shot name: the standard filename
``YYYY-MM-DD_SSSS_<script>_<n>.h5`` carries everything needed to rebuild its
path under labconfig's ``experiment_shot_storage``, which is runmanager's
``output_folder_format``.

Reconstructing the time axis
----------------------------
The NI tables hold one row per clock tick, with no timestamps -- the timing
lives in the PrawnBlaster pulse program that clocks each board.  Each
instruction is ``(half_period, reps)`` in ticks of ``clock_frequency``, so tick
times are the cumulative sum of ``reps`` periods of ``2 * half_period / f``.
Instructions with ``reps == 0`` are waits and the stop instruction: they
produce no samples and no compile-time duration, which makes the reconstructed
axis labscript's ``t`` rather than wall-clock time.  It lands exactly on the
pseudoclock's ``stop_time`` attribute, which is the arithmetic's check.

Two shots need not share a clock grid -- a changed ramp changes the tick count
-- so channels are compared on the union of the two time axes with a
zero-order hold, which is what the hardware does between ticks anyway.
"""

import argparse
import difflib
import io
import os
import re
import tokenize
from collections import namedtuple

# labscript_utils.h5_lock monkeypatches h5py and refuses to load if h5py got
# there first, so anything that imports lyse must not be the first to import
# it.  Same ordering constraint as analysislib.imaging.process.
try:
    import labscript_utils.h5_lock      # noqa: F401
except ImportError:                     # pragma: no cover
    pass

import h5py
import numpy as np


#: Analog channels differing by less than this are called equal.  The NI 6738
#: is a 16-bit DAC over +-10 V, so one LSB is ~0.3 mV; this sits well below
#: that and exists only to stop float32 round-trips showing up as changes.
ANALOG_ATOL = 1e-6

#: Connection-table classes that carry a per-channel output table.
OUTPUT_CLASSES = ('AnalogOut', 'DigitalOut', 'Shutter', 'Trigger', 'StaticAnalogOut')

#: Classes whose values are logic levels, compared exactly rather than to atol.
DIGITAL_CLASSES = ('DigitalOut', 'Shutter', 'Trigger')

SHOT_NAME_RE = re.compile(
    r'^(?P<y>\d{4})-(?P<m>\d{2})-(?P<d>\d{2})_(?P<seq>\d{4})_(?P<script>.+)_\d+$'
)

#: One output's waveform.  ``ticks`` are clock ticks (see ``Shot.tick_times``),
#: integral so that two shots' axes can be unioned exactly; ``clocked`` says
#: they convert to seconds, and ``static`` marks an output with no time axis
#: at all, held for the whole shot.
Channel = namedtuple('Channel', 'ticks values port klass clocked static')


# -- locating shots --------------------------------------------------------

def resolve_shot(spec, storage=None):
    """Return a shot path from a full path or a bare shot name.

    A bare ``2026-09-15_0012_cs_molasses_healthcheck_59`` expands to
    ``<storage>/<script>/<year>/<month>/<day>/<sequence>/<name>.h5`` -- the
    layout runmanager's ``output_folder_format`` writes and
    ``imaging.portal.sequence_folder`` reads.
    """
    if os.path.exists(spec):
        return spec
    name = os.path.basename(spec)
    if name.endswith('.h5'):
        name = name[:-3]
    stem = re.sub(r'_rep\d+$', '', name)
    match = SHOT_NAME_RE.match(stem)
    if match is None:
        raise FileNotFoundError(
            f'{spec!r} is not an existing path, and does not look like a shot '
            'name of the form YYYY-MM-DD_SSSS_<script>_<n>'
        )
    if storage is None:
        from labscript_utils.labconfig import LabConfig
        storage = LabConfig().get('DEFAULT', 'experiment_shot_storage')
    path = os.path.join(storage, match['script'], match['y'], match['m'],
                        match['d'], match['seq'], name + '.h5')
    if not os.path.exists(path):
        raise FileNotFoundError(f'{spec!r} resolved to {path}, which does not exist')
    return path


# -- reading a shot --------------------------------------------------------

def _decode(value):
    return value.decode() if isinstance(value, bytes) else value


class Shot:
    """One shot file, with the pieces a diff needs pulled out and named.

    Everything is read in ``__init__`` and the file closed again: the tables
    are small, a few thousand rows, and holding an h5py handle open across a
    long notebook session is how you end up fighting the lock.
    """

    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path)
        self.stop_time = float('nan')
        self.clock_frequency = None
        with h5py.File(path, 'r') as f:
            self.attrs = {k: _decode(v) for k, v in f.attrs.items()}
            self.script = f['script'][()].decode() if 'script' in f else ''
            self.script_name = (_decode(f['script'].attrs.get('name', b''))
                                if 'script' in f else '')
            self.has_labscriptlib = 'labscriptlib' in f
            self._read_globals(f)
            self._read_connection_table(f)
            self._read_timing(f)
            self._read_devices(f)
        self._build_channels()

    # globals ..............................................................

    def _read_globals(self, f):
        # Evaluated values live on the /globals group itself; the raw
        # expressions live on its per-group subgroups.  See
        # runmanager.make_single_run_file.
        self.evaluated = {}
        for name, value in f['globals'].attrs.items():
            if isinstance(value, h5py.Reference) and not value:
                value = None                    # how runmanager stores a None
            self.evaluated[name] = value
        self.raw = {}
        self.group_of = {}
        for group in f['globals']:
            for name, expression in f['globals'][group].attrs.items():
                self.raw[name] = _decode(expression)
                self.group_of[name] = group

    def _read_connection_table(self, f):
        self.connection_table = {}
        for row in f['connection table'][:]:
            entry = {key: _decode(row[key]) for key in row.dtype.names}
            self.connection_table[entry['name']] = entry

    def _read_timing(self, f):
        markers = f['time_markers'][:] if 'time_markers' in f else []
        self.time_markers = [(_decode(m['label']), float(m['time'])) for m in markers]
        waits = f['waits'][:] if 'waits' in f else []
        self.waits = [(_decode(w['label']), float(w['time']), float(w['timeout']))
                      for w in waits]
        self.exposures = {}
        for device in f['devices']:
            if 'EXPOSURES' in f['devices'][device]:
                self.exposures[device] = [
                    (float(e['t']), _decode(e['name']), _decode(e['frametype']),
                     float(e['trigger_duration']))
                    for e in f['devices'][device]['EXPOSURES'][:]
                ]

    def _read_devices(self, f):
        self.tables = {}                 # device -> {dataset name: structured array}
        self.device_attrs = {}
        self.pulse_programs = {}
        for device in f['devices']:
            group = f['devices'][device]
            self.device_attrs[device] = dict(group.attrs)
            self.tables[device] = {}
            for dataset in group:
                data = group[dataset][:]
                if dataset.startswith('PULSE_PROGRAM_'):
                    self.pulse_programs[int(dataset.rsplit('_', 1)[1])] = data
                else:
                    self.tables[device][dataset] = data
        for attrs in self.device_attrs.values():
            if 'clock_frequency' in attrs:
                self.clock_frequency = float(attrs['clock_frequency'])
                self.stop_time = float(attrs.get('stop_time', float('nan')))

    # the clock ............................................................

    def pseudoclock_of(self, device):
        """Index of the pseudoclock clocking ``device``, or None.

        Walks device -> clockline -> pseudoclock through the connection table
        and reads the index out of the pseudoclock's ``parent port``
        (``'pseudoclock 2'``), rather than assuming the clocklines were
        declared in order.
        """
        entry = self.connection_table.get(device)
        if entry is None:
            return None
        clockline = self.connection_table.get(entry['parent'])
        if clockline is None or clockline['class'] != 'ClockLine':
            return None
        pseudoclock = self.connection_table.get(clockline['parent'])
        if pseudoclock is None:
            return None
        match = re.search(r'(\d+)$', pseudoclock['parent port'])
        return int(match.group(1)) if match else None

    def tick_times(self, index):
        """Sample times of pseudoclock ``index``, one per row of its boards' tables.

        Returned in integer clock ticks, not seconds.  Two shots are compared
        by taking the union of their time axes, and a sum of floats does not
        reproduce bit-for-bit down two different instruction lists -- a tick at
        the same instant in both shots would land on 3.19140958 in one and
        3.1914095799999997 in the other, and every such pair would show up as a
        spurious one-sample difference.  The instruction list is integral
        anyway, so keep it that way and divide by ``clock_frequency`` only to
        print.

        ``reps == 0`` instructions are the waits and the stop instruction: no
        samples, and no compile-time duration, so the axis is labscript's ``t``.
        """
        program = self.pulse_programs.get(index)
        if program is None or self.clock_frequency is None:
            return None
        per_tick = np.repeat(2 * program['half_period'].astype(np.int64),
                             program['reps'])
        if not len(per_tick):
            return per_tick
        # A tick happens at the *start* of its period, so shift the sum by one.
        return np.concatenate([[0], np.cumsum(per_tick)[:-1]])

    def seconds(self, ticks):
        """Clock ticks as labscript seconds."""
        return np.asarray(ticks) / self.clock_frequency

    # channels .............................................................

    def _build_channels(self):
        """``{name: Channel}`` for every output in the connection table.

        Digital lines are unpacked out of their port bytes, and static outputs
        get a single sample at t=0, so every channel compares the same way.
        The time axis is in clock ticks; see :meth:`tick_times`.
        """
        self.channels = {}
        self.clock_of_device = {}
        for name, entry in self.connection_table.items():
            if entry['class'] not in OUTPUT_CLASSES:
                continue
            device, port = entry['parent'], entry['parent port']
            tables = self.tables.get(device, {})
            if device not in self.clock_of_device:
                index = self.pseudoclock_of(device)
                self.clock_of_device[device] = (
                    None if index is None else self.tick_times(index))
            times = self.clock_of_device[device]

            static = False
            if 'AO' in tables and port in tables['AO'].dtype.names:
                values = tables['AO'][port].astype(np.float64)
            elif ('STATIC_DATA' in tables
                    and port in tables['STATIC_DATA'].dtype.names):
                values = tables['STATIC_DATA'][port].astype(np.float64)
                times = np.zeros(len(values), dtype=np.int64)
                static = True
            elif 'DO' in tables and '/' in port:
                byte_name, line = port.split('/')
                if byte_name not in tables['DO'].dtype.names:
                    continue
                bit = int(re.search(r'(\d+)$', line).group(1))
                values = ((tables['DO'][byte_name] >> bit) & 1).astype(np.float64)
            else:
                continue

            clocked = static or (times is not None and len(times) == len(values))
            if not clocked:
                # No usable clock for this board: fall back to comparing by
                # sample index, and say so by flagging the axis as unclocked.
                times = np.arange(len(values), dtype=np.int64)
            self.channels[name] = Channel(times, values, f'{device}/{port}',
                                          entry['class'], clocked and not static,
                                          static)


# -- formatting ------------------------------------------------------------

def _fmt(value, width=28):
    """Short, stable repr of a value for a table cell."""
    if isinstance(value, (bytes, np.bytes_)):
        value = value.decode()
    if isinstance(value, np.ndarray):
        text = np.array2string(value, threshold=6, precision=6, separator=',')
    elif isinstance(value, float):
        text = f'{value:.10g}'
    else:
        text = str(value)
    text = ' '.join(text.split())
    return text if len(text) <= width else text[:width - 1] + '~'


def _table(headers, rows, indent='  ', max_width=44):
    """Fixed-width text table.  Not pandas: it truncates columns by terminal width."""
    if not rows:
        return ''
    rows = [[_clip(cell, max_width) for cell in row] for row in rows]
    columns = [[str(h)] + [str(r[i]) for r in rows] for i, h in enumerate(headers)]
    widths = [max(len(cell) for cell in column) for column in columns]
    lines = [indent + '  '.join(str(h).ljust(w)
                                for h, w in zip(headers, widths)).rstrip(),
             indent + '  '.join('-' * w for w in widths)]
    for row in rows:
        lines.append(indent + '  '.join(str(c).ljust(w)
                                        for c, w in zip(row, widths)).rstrip())
    return '\n'.join(lines)


def _clip(cell, width):
    """One cell, kept to ``width``: a single long value must not widen a table."""
    text = str(cell)
    return text if len(text) <= width else text[:width - 3] + '...'


def _heading(text):
    return f'\n-- {text} ' + '-' * max(0, 74 - len(text))


# -- globals ---------------------------------------------------------------

def _tokenify(expression):
    """Tokens of an expression, ignoring comments and whitespace.

    The same filter runmanager's globals diff applies: a reworded comment or a
    reflowed expression is not a change worth reporting.
    """
    junk = {tokenize.COMMENT, tokenize.NL, tokenize.NEWLINE,
            tokenize.INDENT, tokenize.DEDENT, tokenize.ENDMARKER}
    try:
        return tuple((kind, value) for kind, value, _, _, _
                     in tokenize.generate_tokens(io.StringIO(expression).readline)
                     if kind not in junk)
    except (tokenize.TokenError, IndentationError, SyntaxError):
        return ('<unparsed>', expression)


def _values_equal(a, b):
    if isinstance(a, np.ndarray) or isinstance(b, np.ndarray):
        return np.array_equal(np.asarray(a), np.asarray(b))
    try:
        return bool(a == b)
    except ValueError:                                  # pragma: no cover
        return False


def diff_globals(a, b):
    """Rows for globals whose evaluated value *and* raw expression both differ.

    Requiring both keeps out the two standing false positives: an expression
    edited to the same value, and a value whose type has no sane ``__eq__``.
    """
    rows = []
    for name in sorted(set(a.evaluated) | set(b.evaluated)):
        in_a, in_b = name in a.evaluated, name in b.evaluated
        if in_a and in_b and _values_equal(a.evaluated[name], b.evaluated[name]):
            continue
        raw_a = a.raw.get(name, '-')
        raw_b = b.raw.get(name, '-')
        if in_a and in_b and _tokenify(raw_a) == _tokenify(raw_b):
            continue
        rows.append([
            name,
            a.group_of.get(name, b.group_of.get(name, '')),
            _fmt(a.evaluated[name]) if in_a else '(absent)',
            _fmt(b.evaluated[name]) if in_b else '(absent)',
            _fmt(raw_a, 22), _fmt(raw_b, 22),
        ])
    return rows


# -- hardware --------------------------------------------------------------

def _zero_order_hold(ticks, values, query):
    """Value of a sampled-and-held waveform at the ``query`` ticks.

    Between ticks the hardware holds its last value, so that is what a shot
    compiled on a different clock grid should be compared against.
    """
    index = np.clip(np.searchsorted(ticks, query, side='right') - 1,
                    0, len(values) - 1)
    return values[index]


def diff_channels(a, b, atol=ANALOG_ATOL):
    """Per-channel comparison on the union of the two clock grids.

    Returns ``(rows, n_channels)``: one row per channel that moved, saying
    where it first differs, by how much, and over how much of the shot.
    """
    # When the two shots have different stop_times, the end-of-sequence restore
    # slides by that much, and every channel it touches shows a difference in
    # the last few ms that says nothing about the sequence.  Flag differences
    # confined to that window so they can be read past; on a shot whose length
    # changed they are most of the table.
    tail_start = min(a.stop_time, b.stop_time) - abs(a.stop_time - b.stop_time)

    rows = []
    names = sorted(set(a.channels) | set(b.channels))
    for name in names:
        if name not in a.channels or name not in b.channels:
            present = a.channels.get(name) or b.channels[name]
            rows.append((-1.0, [name, present.port,
                                'A only' if name in a.channels else 'B only',
                                '', '', '']))
            continue
        channel_a, channel_b = a.channels[name], b.channels[name]
        if channel_a.port != channel_b.port:
            rows.append((-1.0, [name, f'{channel_a.port} -> {channel_b.port}',
                                'rewired', '', '', '']))
            continue
        grid = np.union1d(channel_a.ticks, channel_b.ticks)
        on_a = _zero_order_hold(channel_a.ticks, channel_a.values, grid)
        on_b = _zero_order_hold(channel_b.ticks, channel_b.values, grid)
        delta = np.abs(on_b - on_a)
        differs = delta > (0 if channel_a.klass in DIGITAL_CLASSES else atol)
        if not differs.any():
            continue
        first = int(np.argmax(differs))
        if channel_a.static:
            when, where = 0.0, 'static'
        elif channel_a.clocked:
            when = grid[first] / a.clock_frequency
            where = f'{when:.6f}'
            if a.stop_time != b.stop_time and when >= tail_start - 1e-9:
                where += '  (shot-end shift)'
        else:
            when, where = 0.0, f'sample {grid[first]}'   # no clock for this board
        rows.append((when, [
            name, channel_a.port, where,
            f'{on_a[first]:.4g} -> {on_b[first]:.4g}',
            f'{delta.max():.4g}',
            f'{int(differs.sum())}/{len(grid)}',
        ]))
    # Chronological, so the report reads forwards through the sequence and the
    # first thing that moved is the first thing you see.
    rows.sort(key=lambda row: row[0])
    return [row for _, row in rows], len(names)


# -- the report ------------------------------------------------------------

def diff_shots(shot_a, shot_b, storage=None, full_script=False,
               all_channels=False, context=3):
    """Compare two shots and return the report as a string.

    ``shot_a`` and ``shot_b`` are paths or bare shot names (see
    :func:`resolve_shot`).  ``full_script`` keeps the whole script diff rather
    than the first hunks; ``all_channels`` also lists what did not change.
    """
    a = Shot(resolve_shot(shot_a, storage))
    b = Shot(resolve_shot(shot_b, storage))
    out = ['=' * 78,
           f'A  {a.name}',
           f'B  {b.name}',
           f'   run time   {a.attrs.get("run time", "?")}'
           f'   ->   {b.attrs.get("run time", "?")}',
           f'   script     {a.script_name or a.attrs.get("script_basename", "?")}'
           f'   ->   {b.script_name or b.attrs.get("script_basename", "?")}',
           '=' * 78]

    # globals
    global_rows = diff_globals(a, b)
    out.append(_heading(f'Globals: {len(global_rows)} changed of {len(a.evaluated)}'))
    out.append(_table(['global', 'group', 'A (eval)', 'B (eval)',
                       'A (raw)', 'B (raw)'], global_rows)
               if global_rows else '  identical')

    # script
    diff = list(difflib.unified_diff(a.script.splitlines(), b.script.splitlines(),
                                     fromfile=f'A/{a.script_name}',
                                     tofile=f'B/{b.script_name}',
                                     n=context, lineterm=''))
    out.append(_heading(f'Script: {len(a.script.splitlines())} lines'))
    if not diff:
        out.append('  identical')
    else:
        shown = diff if full_script else diff[:60]
        out.extend('  ' + line for line in shown)
        if len(shown) < len(diff):
            out.append(f'  ... {len(diff) - len(shown)} more diff lines '
                       '(pass full_script=True)')
    if not (a.has_labscriptlib and b.has_labscriptlib):
        out.append('  note: no /labscriptlib in these shots, so only the top-level '
                   'script is stored;')
        out.append('        changes inside imported subsequence modules are invisible '
                   'here.')

    # timing
    out.append(_heading('Timing'))
    timing_rows = []
    if a.stop_time != b.stop_time:
        timing_rows.append(['stop_time', f'{a.stop_time:.6f}', f'{b.stop_time:.6f}',
                            f'{b.stop_time - a.stop_time:+.6f}'])
    markers_a, markers_b = dict(a.time_markers), dict(b.time_markers)
    for label in dict.fromkeys(list(markers_a) + list(markers_b)):
        ta, tb = markers_a.get(label), markers_b.get(label)
        if ta is None or tb is None or abs(ta - tb) > 1e-9:
            timing_rows.append([
                label,
                '(absent)' if ta is None else f'{ta:.6f}',
                '(absent)' if tb is None else f'{tb:.6f}',
                '' if ta is None or tb is None else f'{tb - ta:+.6f}',
            ])
    if a.waits != b.waits:
        timing_rows.append(['waits', str(a.waits), str(b.waits), ''])
    # One row per camera frame rather than one per camera: a whole EXPOSURES
    # table printed as a tuple is unreadable, and it is the individual trigger
    # times that matter.
    for device in sorted(set(a.exposures) | set(b.exposures)):
        frames_a = {(e[1], e[2]): e for e in a.exposures.get(device, [])}
        frames_b = {(e[1], e[2]): e for e in b.exposures.get(device, [])}
        for key in dict.fromkeys(list(frames_a) + list(frames_b)):
            fa, fb = frames_a.get(key), frames_b.get(key)
            if fa == fb:
                continue
            label = f'{device} {key[0]}/{key[1]}'
            timing_rows.append([
                label,
                '(absent)' if fa is None else f'{fa[0]:.6f}',
                '(absent)' if fb is None else f'{fb[0]:.6f}',
                '' if fa is None or fb is None else f'{fb[0] - fa[0]:+.6f}',
            ])
    out.append(_table(['marker', 'A (s)', 'B (s)', 'delta'], timing_rows)
               if timing_rows
               else '  identical: same stop_time, markers, waits and exposures')

    # hardware
    channel_rows, n_channels = diff_channels(a, b)
    out.append(_heading(
        f'Hardware channels: {len(channel_rows)} changed of {n_channels}'))
    out.append(_table(['channel', 'device/port', 'first delta @ t (s)',
                       'A -> B there', 'max |delta|', 'samples'], channel_rows)
               if channel_rows
               else '  identical: every output table matches sample for sample')
    if all_channels:
        unchanged = sorted((set(a.channels) & set(b.channels))
                           - {row[0] for row in channel_rows})
        out.append(_heading(f'Unchanged channels: {len(unchanged)}'))
        out.append('  ' + ', '.join(unchanged))

    out.append(_heading('Summary'))
    out.append(f'  {len(global_rows)} globals differ, '
               f'script {"differs" if diff else "identical"}, '
               f'{len(channel_rows)} of {n_channels} hardware channels differ.')
    return '\n'.join(out) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(
        description='Diff two labscript shots: globals, script, hardware output.')
    parser.add_argument('shot_a', help='path or bare shot name')
    parser.add_argument('shot_b', help='path or bare shot name')
    parser.add_argument('--storage', default=None,
                        help='shot tree root (default: labconfig experiment_shot_storage)')
    parser.add_argument('--full-script', action='store_true',
                        help='print the whole script diff, not just the first hunks')
    parser.add_argument('--all-channels', action='store_true',
                        help='also list the channels that did not change')
    parser.add_argument('--out', default=None, help='also write the report to a file')
    args = parser.parse_args(argv)

    report = diff_shots(args.shot_a, args.shot_b, storage=args.storage,
                        full_script=args.full_script,
                        all_channels=args.all_channels)
    print(report)
    if args.out:
        with open(args.out, 'w', encoding='utf-8') as f:
            f.write(report)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
