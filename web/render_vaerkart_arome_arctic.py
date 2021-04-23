#!/usr/bin/env python
# -*- encoding: utf8

import codecs
from jinja2 import FileSystemLoader, Environment
from datetime import datetime as dt, timedelta as td

from settings.common import basepath, plotpath
from current_fc_arome import *
from plotdomains import plotdomains



# Where to save the weather map; 
filepath = plotpath+'/../vaerkart_arome_arctic.html'

env = Environment(loader=FileSystemLoader(searchpath=basepath+'/web'))


# The only free parameter for the entire script
date_base = get_current_plotted_fc_arome()
# Override 
#date_base = dt(2015,2,3,0)

print('Creating page for forecasts from %s.' % date_base.strftime('%d.%m.%Y, %H UTC'))



class variable(object):
    def __init__(self, name, units, level):
        self.name = name
        self.units = units
        self.level = level

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
t2 = variable(u'2m Temperature', u'°C', u'')
ff10 = variable(u'10 m wind speed', 'm/s', u'')
tp = variable(u'Precipitiation', 'mm/h', u'')
rh2 = variable(u'2m Relative humidity', '%', u'')
t850 = variable(u'Temperature', u'°C', u'850 hPa')
t925 = variable(u'Temperature', u'°C', u'925 hPa')
q850 = variable(u'Specific humidity', u'g/kg', u'850 hPa')
q925 = variable(u'Specific humidity', u'g/kg', u'925 hPa')
w850 = variable(u'Vertical wind', u'm/s', '850 hPa')
w500 = variable(u'Vertical wind', u'm/s', '500 hPa')
w700 = variable(u'Vertical wind', u'm/s', '700 hPa')
tshff = variable(u'Total Surface heat flux', u'W/m²', u'')


msl = variable(u'Sea level pressure', 'hPa', u'')
barbs10 = variable(u'10 m Wind barbs', u'm/s', u'')
barbs500 = variable(u'Wind barbs', u'm/s', u'500 hPa')
barbs700 = variable(u'Wind barbs', u'm/s', u'700 hPa')
barbs850 = variable(u'Wind barbs', u'm/s', u'850 hPa')
barbs925 = variable(u'Wind barbs', u'm/s', u'925 hPa')
ff925 = variable(u'Wind speed', u'm/s', u'925 hPa')
frovo850 = variable(u'Frontal volumes', '', '850 hPa')
sic = variable(u'Sea ice concentration', '', u'')
sst = variable(u'Sea surface temperature', '°C', u'')

o = overlay
plotlist = [
    plot(u't2m_msl', t2, [o('black dashes', t2, [0,]), o('black', msl, 2)],
        name='2m Temperature and SLP'),
    plot(u't925_msl', t925, [o('black dashes', t925, [0,]), o('black', msl, 5), o('black', barbs925, None)],
        name='925 hPa Temperature, SLP and wind barbs'),
    plot(u't850_msl', t850, [o('black dashes', t850, [0,]), o('black', msl, 5), o('black', barbs850, None)],
        name='850 hPa Temperature, SLP and wind barbs'),
    plot(u'q925_msl', q925, [o('dark red', t850, [-5,]), o('black', msl, 5), o('black', barbs925, None)],
        name='925 hPa Specific humidity, SLP and wind barbs'),
    plot(u'q850_msl', q850, [o('dark red', t850, [-5,]), o('black', msl, 5), o('black', barbs850, None)],
        name='850 hPa Specific humidity, SLP and wind barbs'),
    plot(u'w850_ff', w850, [o('blue shading', ff925, 5), ], 
        name='850 hPa Vertical wind and 925 hPa wind speed'),
    plot(u'w500_winds', w500, [o('black', barbs500, None), ], 
        name='500 hPa Vertical wind and wind barbs'),
    plot(u'w700_winds', w700, [o('black', barbs700, None), ], 
        name='700 hPa Vertical wind and wind barbs'),
    plot(u'ff10_fronts', ff10, [o('blue shading', frovo850, None), o('black', barbs10, None)],
        name='10m wind speed, barbs and frontal volumes at 850 hPa'),
    plot(u'rh2m_tp', tp, [o('grey shading', rh2, [20, 40, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 99]), o('violet', sic, [0.2, 0.8] )], 
        name='2m Relative humidity, precipitation and MIZ'),
    plot(u'shf_wind', tshff, [o('grey', sst, 1), o('violet', sic, [0.2, 0.8] ), o('yellow, orange, red', ff10, [17.2, 24.5, 32.7] )], 
        name='Surface fluxes, 10m winds, SSTs, and MIZ'),
]

fclist = [date_base - td(0.25)*i for i in range(29)]
date_fc = fclist[0]

leadlist = range(0,67,3)
leadlist_link = range(0,67,6)

timlist = [date_fc + td(0,3600*lead) for lead in leadlist]


# Rendering
t = env.get_template('template_jinja.html')
c = { 
    'plot_domains': plotdomains,
    'plot_domain': plotdomains[12][0],
    'plot_prefix': 'no_for_arctic',
    'plotlist': plotlist, 
    'timlist': timlist,
    'leadlist': leadlist,
    'leadlist_link': leadlist_link,
    'fclist': fclist, 
    'initplot': plotlist[0],
    'date_begin': date_fc,
    'date_init': date_fc,
    'plotdir': 'plots',
    'display_details': False,
}

f = codecs.open(filepath, mode='w', encoding='utf-8')
f.write(t.render(**c))
f.close()

# the end
