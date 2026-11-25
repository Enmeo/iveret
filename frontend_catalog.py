#!/usr/bin/env python
# -*- encoding: utf-8
#
# Catalogue of the new iveret frontend (B1)
#
# write_catalog() exports meta/catalog.json below WEB_ROOT: the sources,
# domains, plot types with their legend text, lead times and archive settings
# the frontend needs to address and describe the plots. The shape is defined
# in the frontend repository (doc/backend-interface.md, src/catalog/types.ts).
#
# Plot titles, legend text, the plots per (source, domain) and the figure
# sizes come from plotconfig.py and plotconfig_ihavet.py. Sources, time axes
# and the archive are not part of the plot configuration and are listed by
# hand below; keep them in sync with the plot_forecast*.py scripts
# (leadlist, leadlist_link), current_fc*.py (init hours) and cleanup.py.
#
# The catalogue only depends on the configuration, so writing it is
# idempotent. Every pipeline calls write_catalog(); the file is only replaced
# when its content changed, so its Last-Modified/ETag stay stable.
#
# Derived from frontend/tools/make_catalog.py.

import json
import os

from settings.common2 import WEB_ROOT, FILETYPE, SAVE_DPI


CATALOG_PATH = f'{WEB_ROOT}/meta/catalog.json'

# Relative to the data base URL of the frontend; /maps is served from WEB_ROOT/plots
PLOT_URL = 'maps/{domain}/{plot}/{srcdir}/{init}_for_{valid}.' + FILETYPE

# key: (label, directory in plot path, status file name, init hours UTC, stale threshold override)
SOURCES = {
    'ec':      ('ECMWF IFS', 'ec', 'ecmwf', [0, 12], None),
    'aifs':    ('ECMWF AIFS', 'ec', 'ecmwf', [0, 12], None),
    'ec_ext':  ('ECMWF extended range', 'ec_ext', 'ecmwf_ext', [0], 42),
    'noaa':    ('GFS', 'noaa', 'gfs', [0, 6, 12, 18], None),
    'no':      ('AROME', 'no', 'arome', [0, 6, 12, 18], None),
    'dmi':     ('DMI HARMONIE', 'dmi', 'dmi', [0, 6, 12, 18], None),
    'no_kyst': ('NorKyst (ocean)', 'no_kyst', 'kyst', [0], None),
}

# key: (label, kind); the order is the order of the domain selector
DOMAINS = {
    'natl':       ('North Atlantic', 'map'),
    'npolar':     ('Northern Hemisphere', 'map'),
    'spolar':     ('Southern Hemisphere', 'map'),
    'tindpac':    ('Tropical Indo-Pacific', 'map'),
    'nordicseas': ('Nordic Seas', 'map'),
    'atlarctic':  ('Atlantic Arctic', 'map'),
    'ff_kh':      ('RV Kronprins Haakon', 'map'),
    'scandes':    ('Scandinavia', 'map'),
    'barents':    ('Barents Sea', 'map'),
    'snorway':    ('Southern Norway', 'map'),
    'vestland':   ('Vestland', 'map'),
    'bergen':     ('Bergen', 'map'),
    'dmi':        ('Northwestern Europe', 'map'),
    'we60':       ('Cross section 60°N', 'section'),
}
# Figure sizes (inches, including the colour bar) of domains that are not in
# plotconfig.domains; keep in sync with plotter.figsize in plot_forecast_arome_section.py
EXTRA_FIG_SIZES = {'we60': (10.6667, 4.8)}

LEADS_10DAY = list(range(0, 72, 3)) + list(range(72, 241, 6))
TICKS_10DAY = list(range(0, 241, 12))
TIME_AXES = {   # name: (leads, lead ticks)
    '10day':  (LEADS_10DAY, TICKS_10DAY),
    'aifs':   (list(range(6, 241, 6)), list(range(12, 241, 12))),
    'ec_reg': (list(range(0, 73, 3)), list(range(0, 73, 6))),
    'ext':    (list(range(0, 841, 12)), [24 * (w * 7 + d) for w in range(5) for d in (0, 2, 4)] + [840]),
    'arome':  (list(range(0, 67, 3)), list(range(0, 67, 6))),
    'dmi':    (list(range(0, 61, 3)), list(range(0, 61, 6))),
    'kyst':   (list(range(0, 121, 3)), list(range(0, 121, 12))),
}

# (source in the frontend, domain): (source key in plotconfig.plots, time axis)
PRODUCTS = {}
for _d in ('natl', 'npolar', 'spolar', 'tindpac', 'nordicseas', 'atlarctic', 'ff_kh'):
    PRODUCTS['ec', _d] = ('ec', '10day')
for _d in ('scandes', 'barents'):
    PRODUCTS['ec', _d] = ('ec_local', 'ec_reg')
for _d in ('npolar', 'spolar'):
    PRODUCTS['ec_ext', _d] = ('ec_ext', 'ext')
for _d in ('natl', 'npolar', 'spolar'):
    PRODUCTS['noaa', _d] = ('noaa', '10day')
for _d in ('vestland', 'snorway', 'scandes', 'we60'):
    PRODUCTS['no', _d] = ('no', 'arome')
PRODUCTS['no', 'barents'] = ('no_arctic', 'arome')
for _d in ('vestland', 'snorway', 'dmi'):
    PRODUCTS['dmi', _d] = ('dmi', 'dmi')
for _d in ('bergen', 'vestland', 'snorway'):
    PRODUCTS['no_kyst', _d] = ('no_kyst', 'kyst')

# Plot types filed under one source that the frontend shows as a source of
# their own: plot type in plotconfig -> (frontend source, frontend plot key)
SPLIT_OFF = {'z500_msl_aifs': ('aifs', 'z500_msl')}
# Time axis of split-off sources, where it differs from the source they are filed under
SPLIT_OFF_AXES = {'aifs': 'aifs'}

# Permanently kept analysis plots; keep in sync with cleanup.retain_plots
ARCHIVE = {
    ('ec', 'natl'):   {'start': '2017092200', 'stepHours': 12,
                       'plots': ['z500_msl', 't850_msl', 'tcwv', 'iwvt_axis', 'ptpv2_jets']},
    ('ec', 'npolar'): {'start': '2021060200', 'stepHours': 12,
                       'plots': ['z500_msl', 't850_msl', 'tcwv', 'ptpv2_jets']},
}


def _clean(text):
    return text.replace(' (AIFS)', '')


def _variable(v):
    out = {'name': _clean(v.name)}
    if v.units:
        out['units'] = v.units
    if v.level:
        out['level'] = v.level
    if v.addinfo:
        out['info'] = v.addinfo
    return out


def _plotdef(p):
    overlays = []
    for o in p.overlays:
        item = _variable(o.var)
        if isinstance(o.colorlabel, str):
            item['label'] = o.colorlabel
        if o.contour_label:
            item['note'] = o.contour_label
        overlays.append(item)
    out = {'title': _clean(p.name), 'shading': _variable(p.shading)}
    if overlays:
        out['overlays'] = overlays
    return out


def _canonical(definition):
    return json.dumps(definition, sort_keys=True, ensure_ascii=False)


def build_catalog():
    ''' Build the catalogue as a dict from plotconfig and plotconfig_ihavet '''
    import plotconfig
    import plotconfig_ihavet

    cfg_plots = dict(plotconfig.plots)
    cfg_plots.update(plotconfig_ihavet.plots)
    fig_sizes = {k: d.fig_size_deco for k, d in plotconfig_ihavet.domains.items()}
    fig_sizes.update({k: d.fig_size_deco for k, d in plotconfig.domains.items()})
    fig_sizes.update(EXTRA_FIG_SIZES)

    # Collect the products first, then give every distinct plot definition an id
    raw = []   # (source, domain, axis, [(key, dir, definition)])
    for (source, domain), (cfg_source, axis) in PRODUCTS.items():
        own, split = [], {}
        for plot_dir, p in cfg_plots[cfg_source][domain].items():
            if plot_dir in SPLIT_OFF:
                to_source, key = SPLIT_OFF[plot_dir]
                split.setdefault(to_source, []).append((key, plot_dir, _plotdef(p)))
            else:
                own.append((plot_dir, plot_dir, _plotdef(p)))
        raw.append((source, domain, axis, own))
        for to_source, items in split.items():
            raw.append((to_source, domain, SPLIT_OFF_AXES.get(to_source, axis), items))

    # A plot type can differ in detail between products (e.g. contour interval).
    # The most common variant gets the plain id, the others a numbered one.
    variants = {}
    for _, _, _, items in raw:
        for _, plot_dir, definition in items:
            variants.setdefault(plot_dir, {}).setdefault(_canonical(definition), [0, definition])[0] += 1
    def_ids, plots = {}, {}
    for plot_dir, by_text in variants.items():
        ranked = sorted(by_text.items(), key=lambda kv: -kv[1][0])
        for n, (text, (_, definition)) in enumerate(ranked):
            def_id = plot_dir if n == 0 else f'{plot_dir}~{n + 1}'
            def_ids[plot_dir, text] = def_id
            plots[def_id] = definition

    source_order = list(SOURCES)
    domain_order = list(DOMAINS)
    raw.sort(key=lambda r: (domain_order.index(r[1]), source_order.index(r[0])))
    products = []
    for source, domain, axis, items in raw:
        leads, ticks = TIME_AXES[axis]
        entries = []
        for key, plot_dir, definition in items:
            entry = {'key': key}
            def_id = def_ids[plot_dir, _canonical(definition)]
            if def_id != key:
                entry['def'] = def_id
            if plot_dir != key:
                entry['dir'] = plot_dir
            entries.append(entry)
        product = {'domain': domain, 'source': source, 'leads': leads, 'leadTicks': ticks, 'plots': entries}
        if (source, domain) in ARCHIVE:
            product['archive'] = ARCHIVE[source, domain]
        products.append(product)

    sources = {}
    for key, (label, srcdir, status, init_hours, stale) in SOURCES.items():
        sources[key] = {'label': label, 'srcdir': srcdir, 'status': status, 'initHours': init_hours}
        if stale is not None:
            sources[key]['staleAfterHours'] = stale

    # Pixel sizes as matplotlib produces them (rounded down)
    domains = {}
    for key, (label, kind) in DOMAINS.items():
        width, height = fig_sizes[key]
        domains[key] = {'label': label, 'kind': kind,
                'image': [int(width * SAVE_DPI + 1e-6), int(height * SAVE_DPI + 1e-6)]}

    return {'version': 1, 'plotUrl': PLOT_URL, 'sources': sources, 'domains': domains,
            'plots': plots, 'products': products}


def dump_catalog(catalog):
    ''' JSON with one line per entry: readable diffs without thousands of lines '''
    def block(d):
        return '{\n' + ',\n'.join(f'    {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}' for k, v in d.items()) + '\n  }'
    parts = [
        f'  "version": {catalog["version"]}',
        f'  "plotUrl": {json.dumps(catalog["plotUrl"])}',
        f'  "sources": {block(catalog["sources"])}',
        f'  "domains": {block(catalog["domains"])}',
        f'  "plots": {block(catalog["plots"])}',
        '  "products": [\n' + ',\n'.join('    ' + json.dumps(p, ensure_ascii=False) for p in catalog['products']) + '\n  ]',
    ]
    return '{\n' + ',\n'.join(parts) + '\n}\n'


def write_catalog(path=CATALOG_PATH, raise_errors=False):
    ''' Write meta/catalog.json for the new frontend, atomically and only if changed

    Returns True if the file was (re)written. Errors are printed to stderr and
    otherwise ignored unless raise_errors is set, so that a problem with the
    catalogue does not stop a pipeline from rendering the old pages.
    '''
    try:
        return _write_catalog(path)
    except Exception:
        if raise_errors:
            raise
        import sys
        import traceback
        print('Writing the frontend catalogue failed:', file=sys.stderr)
        traceback.print_exc()
        return False


def _write_catalog(path):
    text = dump_catalog(build_catalog())
    json.loads(text)   # sanity check

    try:
        with open(path, encoding='utf-8') as f:
            if f.read() == text:
                return False
    except FileNotFoundError:
        pass

    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmppath = f'{path}.{os.getpid()}.tmp'
    with open(tmppath, 'w', encoding='utf-8') as f:
        f.write(text)
    os.chmod(tmppath, 0o644)
    os.replace(tmppath, path)

    return True


if __name__ == '__main__':
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else CATALOG_PATH
    changed = write_catalog(target, raise_errors=True)
    print(f'{"Wrote" if changed else "Unchanged:"} {target}')


# the end
