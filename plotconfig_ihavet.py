#!/usr/bin/env python
# -*- encoding: utf-8


import copy
import matplotlib as mpl
import codecs
from datetime import datetime as dt, timedelta as td

from dynlib.shorthands import *
from settings.common2 import pconf, pconfl, WEB_ROOT, VAERKART_ROOT

from plotconfig import domain, variable, plot, overlay, render_webpage_factory, datasources, level2plev, plotter

WEB_ROOT += '/ocean'
#
# Central plot configuration for all plots on ihavet
#

# Defining variables
variables = {
    'sst': variable('Sea-surface temperature', '°C', ''),
    'sss': variable('Sea-surface salinity', 'PSU', ''),
    'ffsfc': variable('Surface current speed', 'cm/s', ''),
    'sfccur': variable('Surface currents', '', ''),
    'bathy': variable('Bathymetry', 'm', ''),
}
# Make variables available as local variables as well
g = globals()
for v, vdef in variables.items():
    g[v] = vdef
del g

# Define shorthand for overlays used below
o = overlay

sss_scale = [0, 20, 30, 32, 32.5, 33, 33.3, 33.6, 33.8, 34, 34.2, 34.4, 34.6, 34.8, 35, 35.2, 37]

# Defining standard map setup to be shared across forecast sources and domains
def map_archetypes():
    return {
    'sst_sfccur': plot(sst, scale=np.arange(0,21.1,0.5), ticks=range(0,21,5), overlays=[
        o('dark grey', bathy, [500, 1000, 1500], colors='0.2', linewidths=1, alpha=0.7), 
        o('black', sfccur, None, otype='quiver'), 
    ], name='SST and surface currents'),
    'sss_sfccur': plot(sss, scale=sss_scale, norm=mpl.colors.BoundaryNorm(sss_scale, 256), ticks=sss_scale,
            cb_tickspacing='uniform', extend='neither', overlays=[
        o('light grey', bathy, [500, 1000, 1500], colors='0.9', linewidths=1, alpha=0.7), 
        o('black', sfccur, None, otype='quiver'), 
    ], name='SSS and surface currents'),
    'ff_sfccur': plot(ffsfc, scale=np.arange(0,201,10), ticks=range(0,201,40), overlays=[
        o('light grey', bathy, [500, 1000, 1500], colors='0.9', linewidths=1, alpha=0.7), 
        o('black', sfccur, None, otype='quiver'), 
    ], name='Surface current speed and direction'),
}

def _select_map(plot_names, **kwargs):
    plots = map_archetypes(**kwargs)
    return {plot_name: plots[plot_name] for plot_name in plot_names}

domains = {
    'snorway': domain(proj.S_Norway, (6.4,6.4), (7.27273,6.4), vector_space_interval=20),
    'vestland': domain(proj.Vestland, (6.4,6.4), (7.27273,6.4), vector_space_interval=10),
    'bergen': domain(proj.Bergen, (6.4,6.4), (7.27273,6.4), vector_space_interval=2),
}

plots = {
    'no_kyst': {
        'bergen': _select_map(['sst_sfccur', 'sss_sfccur', 'ff_sfccur', ]),
        'vestland': _select_map(['sst_sfccur', 'sss_sfccur', 'ff_sfccur', ]),
        'snorway': _select_map(['sst_sfccur', 'sss_sfccur', 'ff_sfccur', ]),
    },
}

# (How) Can this be derived from the plot defintions above?
pages = {
    ('no_kyst', 'bergen'): ('NorKyst forecasts Bergen', '/vaerkart_kyst_bergen.html'),
    ('no_kyst', 'vestland'): ('NorKyst forecasts Vestland', '/vaerkart_kyst_vestland.html'),
    ('no_kyst', 'snorway'): ('NorKyst forecasts Southern Norway', '/vaerkart_kyst.html'),
}

plots_per_page = {
    ('no_kyst', 'bergen'): plots['no_kyst']['bergen'],
    ('no_kyst', 'vestland'): plots['no_kyst']['vestland'],
    ('no_kyst', 'snorway'): plots['no_kyst']['snorway'],
}

del o

render_webpage = render_webpage_factory(pages, plots_per_page, web_root=WEB_ROOT)


# C'est le fin
