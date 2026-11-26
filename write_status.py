#!/usr/bin/env python
# -*- encoding: utf-8
#
# Status files of the new iveret frontend (B2, B5)
#
# Each pipeline (plot_n_update*.sh) calls this script when the plots of a run
# are complete. It maintains WEB_ROOT/meta/status/<name>.json:
#
#   {
#     "version": 1,
#     "updated": "2026-11-10T07:42:00Z",
#     "inits": ["2026111000", "2026110912", ...],             newest first
#     "partial": {"2026111000": ["cycfreq_msl", "meteograms"]}  optional
#   }
#
# `inits` lists the runs that have been reported as plotted, newest first,
# at most `keep` of them (the number of runs the old pages offered). Runs
# whose plots have been deleted in the meantime (cleanup.py) are dropped, so
# the list stays honest about gaps and deletions. When the JSON file does not
# exist yet, the list is seeded from the plots on disk.
#
# `partial` lists, per init, plot types that follow later than the rest of the
# run (B5). They are reported with --partial when the run is marked as
# plotted, and removed again with --complete once they are there.
#
# Usage:
#   write_status.py <name> <init> [--partial plot[,plot...]] [--complete plot[,plot...]]
#
# <init> may be given in any of the formats of the current_fc*.py scripts
# (2026111000, 20261110T00Z, 2026-11-10T00:00:00Z).
#
# The file is written atomically; concurrent calls for the same pipeline are
# serialised with a lock file.

import argparse
import fcntl
import json
import os
import re
import sys
from datetime import datetime as dt, timedelta as td, timezone

from settings.common2 import WEB_ROOT, plotpath


STATUS_DIR = f'{WEB_ROOT}/meta/status'
DATEFMT = '%Y%m%d%H'

# Per pipeline (status name in frontend_catalog.SOURCES):
#   keep: maximum number of listed runs; as the fclist of the old pages
#   cadence: hours between runs; used to seed the list from the plots on disk
#   ref: (domain, plot type, source directory, lead time in h) of a plot that
#        every run has. It is used to detect runs whose plots have been
#        deleted. Use an early lead time that is not kept in the archive.
PIPELINES = {
    'ecmwf':     dict(keep=15, cadence=12, ref=('natl', 'z500_msl', 'ec', 3)),
    'ecmwf_ext': dict(keep=21, cadence=24, ref=('npolar', 'prob_t850', 'ec_ext', 12)),
    'arome':     dict(keep=29, cadence=6, ref=('vestland', 't2m_msl', 'no', 3)),
    'dmi':       dict(keep=29, cadence=6, ref=('vestland', 't2m_msl', 'dmi', 3)),
    'gfs':       dict(keep=31, cadence=6, ref=('natl', 'z500_msl', 'noaa', 3)),
    'kyst':      dict(keep=5, cadence=24, ref=('snorway', 'sst_sfccur', 'no_kyst', 3)),
}

# Plots made before the switch to WebP may still be PNG
PLOT_EXTENSIONS = ('webp', 'png')


def parse_init(text):
    ''' Accept YYYYmmddHH, YYYYmmddTHHZ, YYYY-mm-ddTHH:MM:SSZ and similar '''
    digits = re.sub(r'\D', '', text)
    if len(digits) < 10:
        raise ValueError(f'Cannot parse init time `{text}`.')
    return dt.strptime(digits[:10], DATEFMT)


def ref_plot_exists(name, init):
    ''' Whether the reference plot of the pipeline exists for this init '''
    domain, plot, srcdir, lead = PIPELINES[name]['ref']
    base = f'{plotpath}/{domain}/{plot}/{srcdir}/{init.strftime(DATEFMT)}_for_{(init + td(hours=lead)).strftime(DATEFMT)}'
    return any(os.path.exists(f'{base}.{ext}') for ext in PLOT_EXTENSIONS)


def ref_dir_exists(name):
    domain, plot, srcdir, lead = PIPELINES[name]['ref']
    return os.path.isdir(f'{plotpath}/{domain}/{plot}/{srcdir}')


def seed_inits(name, newest):
    ''' Runs found on disk, going back `keep` runs from `newest` '''
    keep, cadence = PIPELINES[name]['keep'], PIPELINES[name]['cadence']
    candidates = [newest - td(hours=cadence * i) for i in range(1, keep)]
    return [init for init in candidates if ref_plot_exists(name, init)]


def read_status(path):
    try:
        with open(path, encoding='utf-8') as f:
            status = json.load(f)
    except FileNotFoundError:
        return None
    except ValueError:
        print(f'Ignoring unreadable status file {path}.', file=sys.stderr)
        return None

    inits = [parse_init(s) for s in status.get('inits', [])]
    partial = {parse_init(k): list(v) for k, v in status.get('partial', {}).items()}
    return inits, partial


def update_status(name, init, add_partial=(), complete=()):
    ''' Record `init` as plotted for pipeline `name` and rewrite its status file '''
    if name not in PIPELINES:
        raise ValueError(f'Unknown pipeline `{name}`, expected one of {", ".join(PIPELINES)}.')

    os.makedirs(STATUS_DIR, exist_ok=True)
    path = f'{STATUS_DIR}/{name}.json'

    with open(f'{STATUS_DIR}/.{name}.lock', 'w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)

        previous = read_status(path)
        if previous is None:
            inits, partial = seed_inits(name, init), {}
        else:
            inits, partial = previous

        inits = sorted(set(inits) | {init}, reverse=True)

        # Drop runs whose plots are gone; skip this check if the reference
        # plot type is not produced at all (configuration changed)
        if ref_dir_exists(name):
            inits = [i for i in inits if i == init or ref_plot_exists(name, i)]
        else:
            print(f'Reference plot directory of `{name}` not found, not checking for deleted runs.', file=sys.stderr)
        inits = inits[:PIPELINES[name]['keep']]

        pending = set(partial.get(init, [])) | set(add_partial)
        pending -= set(complete)
        if pending:
            partial[init] = sorted(pending)
        else:
            partial.pop(init, None)
        partial = {i: plots for i, plots in partial.items() if i in inits}

        status = {
            'version': 1,
            'updated': dt.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            'inits': [i.strftime(DATEFMT) for i in inits],
        }
        if partial:
            status['partial'] = {i.strftime(DATEFMT): partial[i] for i in sorted(partial, reverse=True)}

        tmppath = f'{path}.{os.getpid()}.tmp'
        with open(tmppath, 'w', encoding='utf-8') as f:
            json.dump(status, f, indent=2)
            f.write('\n')
        os.chmod(tmppath, 0o644)
        os.replace(tmppath, path)

    return status


def _plot_list(text):
    return [p for p in text.split(',') if p]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Update the frontend status file of a pipeline.')
    parser.add_argument('name', choices=list(PIPELINES))
    parser.add_argument('init')
    parser.add_argument('--partial', type=_plot_list, default=[],
            help='comma-separated plot types still missing for this init')
    parser.add_argument('--complete', type=_plot_list, default=[],
            help='comma-separated plot types that are now available for this init')
    args = parser.parse_args()

    status = update_status(args.name, parse_init(args.init), args.partial, args.complete)
    print(f'{args.name}: {len(status["inits"])} runs, newest {status["inits"][0]}')


# the end
