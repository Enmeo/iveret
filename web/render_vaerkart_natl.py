#!/usr/bin/env python
# -*- encoding: utf8

import codecs
from jinja2 import FileSystemLoader, Environment
from datetime import datetime as dt, timedelta as td

from settings.common import basepath, plotpath
from current_fc import *
from current_fc_gfs import *
from mapdomains import mapdomains

from vardefs import *

# Where to save the weather map; 
filepath = plotpath+'/../closed/vaerkart_natl.html'

env = Environment(loader=FileSystemLoader(searchpath=basepath+'/web'))

date_base_ec = get_current_plotted_fc()
date_base_gfs = get_current_plotted_fc_gfs()
# Override
#date_base = dt(2016,10,5,12)

print(f'''Creating page for North Atlantic forecasts, using:
 - ECMWF: {date_base_ec.strftime('%d.%m.%Y, %H UTC')} 
 - GFS: {date_base_gfs.strftime('%d.%m.%Y, %H UTC')} ''' )




o = overlay
plotlist = {
    ('ECMWF', 'ec'): [
        plot(u'z500_msl', z500, [o('white', z500, [552,]), o('black', msl, 5)], 
            name='500 hPa Geopotential and SLP'), 
        plot(u't850_msl', t850, [o('black dashes', t850, [0,]), o('black', msl, 5), o('black', barbs850, None)],
            name='850 hPa Temperature, SLP and wind barbs'),
        plot(u'deform850_fronts', def850, [o('black double-arrows', defang850, None), o('dark cyan shading', frovo850, None), 
            o('red, blue, purple', fronts850, None), o('dark red', t850, [-5,]), ],
            name='850 hPa Deformation, fronts and precipitation'),
        plot(u'sshf_winds', sshff, [o('black', barbs10, None), o('grey', sst, 1), o('light blue', sic, [0.2, 0.8] ), 
            o('yellow, orange, red', ff10, [17.2, 24.5, 32.7] )], 
            name='Sensible heat fluxes, 10 m winds, SSTs and MIZ'),
        plot(u'slhf_winds', slhff, [o('black', barbs10, None), o('grey', sst, 1), o('light blue', sic, [0.2, 0.8] ), 
            o('yellow, orange, red', ff10, [17.2, 24.5, 32.7] )], 
            name='Latent heat fluxes, 10 m winds, SSTs and MIZ'),
        plot(u'tcwv', tcwv, [o('black arrows', icwvt, None), 
            o('magenta', lp, [1,3,10]), o('cyan', cp, [1,3,10]), o('dark red', t850, [-5,]), ],
            name='Total column water vapour, fluxes and precip.'),
        plot(u'tcc', lcc, [o('orange shading', mcc, None), o('white shading', hcc, None)],
            name='Cloud cover'),
        plot(u'pvpt315_irot_wind', pvpt315, [o('black', irbarbspt315, None), ],
            name='315 K Pot. Vorticity and irrot. winds'),
        plot(u'pvpt330_irot_wind', pvpt330, [o('black', irbarbspt330, None), ],
            name='330 K Pot. Vorticity and irrot. winds'),
        plot(u'ptpv2_jets', ptpv2, [o('black', ffpv2, [30, 45, 60, 75, 90]), o('white', jetaxespv2, None)],
            name='PV2 Pot. temperature, jets and wind speed'),
        plot(u't850_perc', t850a, [
                o('black', t850p, ['monthly recurrence']), 
                o('grey', t850p, ['yearly recurrence']), 
                o('white', t850p, ['new record']), ], 
            name='850 hPa Temperature amomalies'),
        plot(u'tcwv_perc', tcwva, [
                o('black', t850p, ['monthly recurrence']), 
                o('grey', t850p, ['yearly recurrence']), 
                o('white', t850p, ['new record']), ], 
            name='Total column water vapour anomalies'),
        plot(u'slope_upper', uslope, [o('black', ffpv2, [30, 45, 60, 75, 90]), ],
            name='Upper-level slopes and tropopause winds'),
        plot(u'slope_lower', lslope, [o('black', ffpv2, [30, 45, 60, 75, 90]), ],
            name='Lower-level slopes and tropopause winds'),
    ],
    ('GFS', 'noaa'): [
        plot(u'z500_msl', z500, [o('white', z500, [552,]), o('black', msl, 5)], 
            name='500 hPa Geopotential and SLP'), 
        plot(u't850_msl', t850, [o('black dashes', t850, [0,]), o('black', msl, 5), o('black', barbs850, None)],
            name='850 hPa Temperature, SLP and wind barbs'),
        plot(u'deform850_fronts', def850, [o('black double-arrows', defang850, None), o('dark cyan shading', frovo850, None), 
            o('red, blue, purple', fronts850, None), o('dark red', t850, [-5,]), ],
            name='850 hPa Deformation, fronts and precipitation'),
        plot(u'sshf_winds', sshff, [o('black', barbs10, None), o('grey', sst, 1), o('light blue', sic, [0.2, 0.8] ), 
            o('yellow, orange, red', ff10, [17.2, 24.5, 32.7] )], 
            name='Sensible heat fluxes, 10 m winds, SSTs and MIZ'),
        plot(u'slhf_winds', slhff, [o('black', barbs10, None), o('grey', sst, 1), o('light blue', sic, [0.2, 0.8] ), 
            o('yellow, orange, red', ff10, [17.2, 24.5, 32.7] )], 
            name='Latent heat fluxes, 10 m winds, SSTs and MIZ'),
        plot(u'tcwv', tcwv, [o('black arrows', icwvt, None), 
            o('magenta', lp, [1,3,10]), o('cyan', cp, [1,3,10]), o('dark red', t850, [-5,]), ],
            name='Total column water vapour, fluxes and precip.'),
        plot(u'tcc', lcc, [o('orange shading', mcc, None), o('white shading', hcc, None)],
            name='Cloud cover'),
        plot(u'ptpv2_jets', ptpv2, [o('black', ffpv2, [30, 45, 60, 75, 90]), o('white', jetaxespv2, None)],
            name='PV2 Pot. temperature, jets and wind speed'),
        plot(u't850_perc', t850a, [
                o('black', t850p, ['monthly recurrence']), 
                o('grey', t850p, ['yearly recurrence']), 
                o('white', t850p, ['new record']), ], 
            name='850 hPa Temperature amomalies'),
        plot(u'tcwv_perc', tcwva, [
                o('black', t850p, ['monthly recurrence']), 
                o('grey', t850p, ['yearly recurrence']), 
                o('white', t850p, ['new record']), ], 
            name='Total column water vapour anomalies'),
]}

# Todo: Generalize!
fclist = [date_base_ec - td(0.5)*i for i in range(11)]
date_fc = fclist[0]

leadlist = list(range(0,72,3))
leadlist.extend(range(72,241,6))

leadlist_link = range(0,241,12)

timlist = [date_fc + td(0,3600*lead) for lead in leadlist]


# Rendering
t = env.get_template('template_new.html')
c = {
    'plot_domains': mapdomains,
    'plot_domain': mapdomains[0][0],
    'plotlist': plotlist, 
    'timlist': timlist,
    'leadlist': leadlist,
    'leadlist_link': leadlist_link,
    'fclist': fclist, 
    'initplot': plotlist['ECMWF', 'ec'][0],
    'initplot_fcsrc': 'ec',
    'date_begin': date_fc,
    'date_init': date_fc,
    'plotdir': '/plots',
    'display_details': False,
    'archive': {
        'start': dt(2017,9,22),
        'plots': ['z500_msl', 't850_msl', 'tcwv'],
        'step': 12,
    },
    'panel_ids': {
        1: 'panel_top_left',
        2: 'panel_top_right',
        3: 'panel_bottom_left',
        4: 'panel_bottom_right',
    },
    'panel_classes': {
        1: 'panel_top panel_left',
        2: 'panel_top panel_right',
        3: 'panel_bottom panel_left',
        4: 'panel_bottom panel_right',
    },
    'panel_styles': {
        1: 'width=100%; display: inline-block;',
        2: 'width=100%; display: none;',
        3: 'width=100%; display: none;',
        4: 'width=100%; display: none;',
    },
}

f = codecs.open(filepath, mode='w', encoding='utf-8')
f.write(t.render(**c))
f.close()

# the end
