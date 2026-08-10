"""
Convert between CSV and runmanager globals h5 files.

CSV format (header row required):
    name,value[,units[,expansion]]

    - name:      Python identifier for the global
    - value:     Python expression string (e.g. "1", "3.14", "5*pi")
    - units:     optional unit label shown in runmanager (default: empty)
    - expansion: optional expansion type for scanning (default: empty)

Usage:
    # Create or overwrite an h5 globals file from CSV:
    python h5_converter.py to-h5 <csv_file> [output.h5] [group_name]

    # Update an existing h5 globals file from CSV (adds/overwrites individual globals):
    python h5_converter.py update <h5_file> <csv_file> [group_name]

    # Export a group from an h5 globals file to CSV:
    python h5_converter.py to-csv <h5_file> <group_name> [output.csv]

    # List all groups and globals in an h5 globals file:
    python h5_converter.py list <h5_file> [group_name]

    # Generate a Python stubs file for IDE type checking:
    python h5_converter.py generate-stubs <h5_file> [output_stubs.py]
    (default output: lics_labscript_apparatus/_globals_stubs.py)

    group_name defaults to the CSV/h5 filename stem where not specified.
"""

import csv
import os
import sys

import h5py


def csv_to_globals_h5(csv_path, h5_path=None, group_name=None):
    """Create a new h5 globals file from a CSV. Overwrites if h5_path exists."""
    if h5_path is None:
        h5_path = os.path.splitext(csv_path)[0] + '.h5'
    if group_name is None:
        group_name = os.path.splitext(os.path.basename(csv_path))[0]

    rows = _read_and_validate_csv(csv_path)

    with h5py.File(h5_path, 'w') as f:
        f.create_group('globals')
        _write_rows(f, group_name, rows)

    print(f"Written {len(rows)} globals to '{h5_path}' (group: '{group_name}')")


def update_globals_h5(h5_path, csv_path, group_name=None):
    """Add or overwrite individual globals in an existing h5 file from a CSV.
    Creates the file or group if they don't exist."""
    if group_name is None:
        group_name = os.path.splitext(os.path.basename(csv_path))[0]

    rows = _read_and_validate_csv(csv_path)

    with h5py.File(h5_path, 'a') as f:
        if 'globals' not in f:
            f.create_group('globals')
        _write_rows(f, group_name, rows)

    print(f"Updated {len(rows)} globals in '{h5_path}' (group: '{group_name}')")


def globals_h5_to_csv(h5_path, group_name, csv_path=None):
    """Export a globals group from an h5 file to CSV."""
    if csv_path is None:
        stem = os.path.splitext(h5_path)[0]
        csv_path = f"{stem}_{group_name}.csv"

    with h5py.File(h5_path, 'r') as f:
        group = f['globals'][group_name]
        values = {k: str(v) for k, v in group.attrs.items()}
        units = {k: str(v) for k, v in group['units'].attrs.items()}
        expansions = {k: str(v) for k, v in group['expansion'].attrs.items()}

    rows = [
        {
            'name': name,
            'value': values[name],
            'units': units.get(name, ''),
            'expansion': expansions.get(name, ''),
        }
        for name in values
    ]

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['name', 'value', 'units', 'expansion'])
        writer.writeheader()
        writer.writerows(rows)

    print(f"Exported {len(rows)} globals to '{csv_path}'")


def list_globals_h5(h5_path, group_name=None):
    """Print all groups and globals in an h5 globals file."""
    with h5py.File(h5_path, 'r') as f:
        groups = list(f['globals'].keys())
        targets = [group_name] if group_name else groups
        for name in targets:
            attrs = dict(f['globals'][name].attrs)
            print(f"[{name}]  ({len(attrs)} globals)")
            for k, v in attrs.items():
                print(f"  {k} = {v}")


def generate_stubs(h5_path, output_path=None):
    """Generate a _globals_stubs.py for IDE type checking from a globals h5 file.

    Reads all globals from the h5 file (auto-detects shot format vs runmanager
    format), evaluates their values, and writes a Python file with typed variable
    declarations. Import it in connection_table.py with:

        from typing import TYPE_CHECKING
        if TYPE_CHECKING:
            from lics_labscript_apparatus._globals_stubs import *
    """
    import ast
    import numpy as np

    if output_path is None:
        package_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_path = os.path.join(package_dir, '_globals_stubs.py')

    with h5py.File(h5_path, 'r') as f:
        globals_grp = f['globals']
        flat_attrs = dict(globals_grp.attrs)
        subgroups = [k for k in globals_grp.keys() if isinstance(globals_grp[k], h5py.Group)]

        if flat_attrs:
            # Shot format: attrs are already evaluated Python values
            raw = {k: v for k, v in flat_attrs.items()}
        elif subgroups:
            # Runmanager format: attrs are expression strings, evaluate them
            raw = {}
            for group_name in subgroups:
                for name, expr in globals_grp[group_name].attrs.items():
                    try:
                        raw[name] = ast.literal_eval(str(expr))
                    except (ValueError, SyntaxError):
                        raw[name] = 0.0  # fall back for complex expressions like "5*pi"
        else:
            raise ValueError(f"No globals found in '{h5_path}'")

    def _type_str(v):
        if isinstance(v, bool):          return 'bool'
        if isinstance(v, np.bool_):      return 'bool'
        if isinstance(v, (int, np.integer)):   return 'int'
        if isinstance(v, (float, np.floating)): return 'float'
        if isinstance(v, (str, bytes, np.str_)): return 'str'
        return 'float'

    def _repr(v):
        if isinstance(v, (np.integer,)):  return repr(int(v))
        if isinstance(v, (np.floating,)): return repr(float(v))
        if isinstance(v, np.bool_):       return repr(bool(v))
        if isinstance(v, bytes):          return repr(v.decode())
        return repr(v)

    lines = [
        "# AUTO-GENERATED — do not edit manually.",
        f"# Regenerate with: python apparatus/globals/h5_converter.py generate-stubs {h5_path}",
        "",
    ]
    for name in sorted(raw):
        v = raw[name]
        lines.append(f"{name}: {_type_str(v)} = {_repr(v)}")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines) + '\n')

    print(f"Generated {len(raw)} stubs → '{output_path}'")


def _read_and_validate_csv(csv_path):
    # utf-8-sig strips a UTF-8 BOM if present (added by Excel/Google Sheets on Windows)
    with open(csv_path, newline='', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise ValueError(f"No data rows found in '{csv_path}'")
    missing = [k for k in ('name', 'value') if k not in rows[0]]
    if missing:
        raise ValueError(
            f"Required column(s) {missing} not found in '{csv_path}'. "
            f"Columns present: {list(rows[0].keys())}"
        )
    return rows


def _ensure_group(f, group_name):
    """Create the group structure if it doesn't already exist."""
    if group_name not in f['globals']:
        group = f['globals'].create_group(group_name)
        group.create_group('units')
        group.create_group('expansion')
    return f['globals'][group_name]


def _write_rows(f, group_name, rows):
    group = _ensure_group(f, group_name)
    units_grp = group['units']
    expansion_grp = group['expansion']
    for row in rows:
        name = row['name'].strip()
        value = str(row['value']).strip()
        units = str(row.get('units', '') or '').strip()
        expansion = str(row.get('expansion', '') or '').strip()
        group.attrs[name] = value
        units_grp.attrs[name] = units
        expansion_grp.attrs[name] = expansion


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(1)

    cmd = args[0]
    if cmd == 'to-h5':
        csv_path = args[1]
        h5_path = args[2] if len(args) > 2 else None
        group_name = args[3] if len(args) > 3 else None
        csv_to_globals_h5(csv_path, h5_path, group_name)
    elif cmd == 'update':
        h5_path = args[1]
        csv_path = args[2]
        group_name = args[3] if len(args) > 3 else None
        update_globals_h5(h5_path, csv_path, group_name)
    elif cmd == 'to-csv':
        h5_path = args[1]
        group_name = args[2]
        csv_path = args[3] if len(args) > 3 else None
        globals_h5_to_csv(h5_path, group_name, csv_path)
    elif cmd == 'list':
        h5_path = args[1]
        group_name = args[2] if len(args) > 2 else None
        list_globals_h5(h5_path, group_name)
    elif cmd == 'generate-stubs':
        h5_path = args[1]
        output_path = args[2] if len(args) > 2 else None
        generate_stubs(h5_path, output_path)
    else:
        print(f"Unknown command '{cmd}'. Expected: to-h5, update, to-csv, list, generate-stubs")
        print(__doc__)
        sys.exit(1)
