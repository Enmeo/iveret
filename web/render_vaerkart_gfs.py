#!/usr/bin/env python
# -*- encoding: utf8

import codecs
from jinja2 import FileSystemLoader, Environment
from datetime import datetime as dt, timedelta as td

from settings.common import basepath, plotpath
from current_fc_gfs import *
from plotdomains import plotdomains


# Where to save the weather map; 
filepath = plotpath+'/../vaerkart.html'

env = Environment(loader=FileSystemLoader(searchpath=basepath+'/web'))


# The only free parameter for the entire script
date_base = get_current_plotted_fc_gfs()
# Override
#date_base = dt(2016,10,5,12)

print('Creating page for forecasts from %s.' % date_base.strftime('%d.%m.%Y, %H UTC'))



# Defining stuff
class variable(object):
    def __init__(self, name, units, level, addinfo=u''):
        self.name = name
        self.units = units
        self.level = level
        self.addinfo = addinfo

        #self.overlays = overlays

class plot(object):
    def __init__(self, prefix, shading, overlays=[], name=None):
        self.prefix = prefix
        self.shading = shading
        self.overlays = overlays
        
        if name:
            self.name = name
        elif self.shading.level:
            self.name = '%s on %s' % (self.shading.name, self.shading.level)
        else:
            self.name = self.shading.name

class overlay(object):
    def __init__(self, color, variable, contours):
        self.color = color
        self.var = variable
        if type(contours) == list:
            self.contours = ', '.join(map(str, contours))
        else:
            self.ci = contours
        


# Defining stuff
z500 = variable(u'Geopotential', u'gpdm', u'500 hPa')
t850 = variable(u'Temperature', u'°C', u'850 hPa')
def850 = variable(u'Deformation', '10⁻⁵/s', u'850 hPa')
ff10 = variable(u'10 m wind speed', 'm/s', u'')
tcwv = variable(u'Total column water vapour', 'kg/m²', u'')
lcc = variable(u'Low cloud cover', '', u'')
mcc = variable(u'Mid-level cloud cover', '', u'')
hcc = variable(u'High cloud cover', '', u'')
pvpt315 = variable(u'Potential vorticity', 'PVU', u'315 K')
pvpt330 = variable(u'Potential vorticity', 'PVU', u'330 K')
ptpv2 = variable(u'Potential temperature', 'K', u'PV 2')
sthff = variable(u'Surface total heat flux', u'W/m²', u'')
sshff = variable(u'Surface sensible heat flux', u'W/m²', u'')
slhff = variable(u'Surface latent heat flux', u'W/m²', u'')

tcwvp = variable(u'Total column water vapour percentiles', u'', u'', u'based on ERA-Interim 1979-2017')
tcwva = variable(u'Total column water vapour anomaly', u'kg/m²', u'', u'based on ERA-Interim 1979-2017')
t850p = variable(u'Temperature percentiles', u'', u'850 hPa', u'based on ERA-Interim 1979-2017')
t850a = variable(u'Temperature anomaly', u'K', u'850 hPa', u'based on ERA-Interim 1979-2017')

msl = variable(u'Sea level pressure', 'hPa', u'')
cp = variable(u'Convective precipitation', 'mm/h', u'')
lp = variable(u'Large-scale precipitation', 'mm/h', u'')
tp = variable(u'Total precipitation', 'mm/h', u'')
sic = variable(u'Sea ice concentration', '', u'')
sst = variable(u'Sea surface temperature', '°C', u'')
frovo850 = variable(u'Frontal volumes', '', '850 hPa')
fronts850 = variable(u'Front lines', '', '850 hPa')
barbs850 = variable(u'Wind barbs', u'm/s', u'850 hPa')
barbs10 = variable(u'10 m Wind barbs', u'm/s', u'')
irbarbspt315 = variable(u'Irrot. wind barbs', u'm/s', u'315 K')
irbarbspt330 = variable(u'Irrot. wind barbs', u'm/s', u'330 K')
ffpv2 = variable(u'Wind speed', u'm/s', u'PV 2')
defang850 = variable(u'Axes of dilatation', u'', u'850 hPa')
icwvt = variable(u'Integrated column water vapour transport', u'', u'')
jetaxespv2 = variable(u'Jet axes', u'', u'PV 2')

o = overlay
plotlist = [
    plot(u'z500_msl', z500, [o('white', z500, [552,]), o('black', msl, 5)], 
        name='500 hPa Geopotential and SLP'), 
    plot(u't850_msl', t850, [o('black dashes', t850, [0,]), o('black', msl, 5), o('black', barbs850, None)],
        name='850 hPa Temperature, SLP and wind barbs'),
    plot(u'deform850_fronts', def850, [o('black double-arrows', defang850, None), o('dark cyan shading', frovo850, None), 
        o('red, blue, purple', fronts850, None), o('dark red', t850, [-5,]), ],
        name='850 hPa Deformation, fronts and precipitation'),
    plot(u'sshf_winds', sshff, [o('black', barbs10, None), o('grey', sst, 2), o('light blue', sic, [0.2, 0.8] ), 
        o('yellow, orange, red', ff10, [17.2, 24.5, 32.7] )], 
        name='Sensible heat fluxes, 10 m winds, SSTs and MIZ'),
    plot(u'slhf_winds', slhff, [o('black', barbs10, None), o('grey', sst, 2), o('light blue', sic, [0.2, 0.8] ), 
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
        name='850 hPa Temperature anomalies'),
    plot(u'tcwv_perc', tcwva, [
            o('black', tcwvp, ['monthly recurrence']), 
            o('grey', tcwvp, ['yearly recurrence']), 
            o('white', tcwvp, ['new record']), ], 
        name='Total column water vapour anomalies'),
]

fclist = [date_base - td(0.25)*i for i in range(29)]
date_fc = fclist[0]

leadlist = get_avail_leads()
leadlist_link = [lead for lead in leadlist if lead % 12 == 0] 

timlist = [date_fc + td(0,3600*lead) for lead in leadlist]


# Rendering
t = env.get_template('template_jinja.html')
c = {
    'plot_domains': plotdomains,
    'plot_domain': plotdomains[0][0],
    'fcsrc': 'noaa',
    'domain': 'natl',
    'plotlist': plotlist, 
    'timlist': timlist,
    'leadlist': leadlist,
    'leadlist_link': leadlist_link,
    'fclist': fclist, 
    'initplot': plotlist[0],
    'date_begin': date_fc,
    'date_init': date_fc,
    'plotdir': 'maps',
    'display_details': False,
}

f = codecs.open(filepath, mode='w', encoding='utf-8')
f.write(t.render(**c))
f.close()

# the end
