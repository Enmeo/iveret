#!/usr/bin/env python
# -*- encoding: utf8

import codecs
from jinja2 import FileSystemLoader, Environment
from datetime import datetime as dt, timedelta as td

from settings.common import basepath, plotpath
from current_fc_kyst import get_current_fc_kyst
from plotdomains_ocean import plotdomains


# Where to save the weather map; 
filepath = plotpath+'/../ocean/vaerkart_kyst.html'

env = Environment(loader=FileSystemLoader(searchpath=basepath+'/web'))


# The only free parameter for the entire script
date_base = get_current_fc_kyst()
# Override 
#date_base = dt(2018,8,23,0)

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
sst = variable(u'SST', u'°C', u'')
sss = variable(u'SSS', u'PSU', u'')
ffsfc = variable(u'Surface current speed', u'cm/s', u'')
sfccur = variable(u'Surface currents', u'', u'')
bathy = variable(u'Bathymetry', u'm', u'')

o = overlay
plotlist = [
    plot(u'sst_sfccur', sst, [o('black', sfccur, None), o('light grey', bathy, [500, 1000, 1500]), ],
        name='SST and surface currents'),
    plot(u'sss_sfccur', sss, [o('black', sfccur, None), o('light grey', bathy, [500, 1000, 1500]), ],
        name='SSS and surface currents'),
    plot(u'ff_sfccur', ffsfc, [o('black', sfccur, None), o('light grey', bathy, [500, 1000, 1500]), ],
        name='Surface current speed and direction'),
]

fclist = [date_base - td(i) for i in range(5)]
date_fc = fclist[0]

leadlist = range(0,67,3)
leadlist_link = range(0,67,6)

timlist = [date_fc + td(0,3600*lead) for lead in leadlist]


# Rendering
t = env.get_template('template_jinja.html')
c = { 
    'plot_domains': plotdomains,
    'plot_domain': plotdomains[2][0],
    'plot_prefix': 'no_kyst',
    'plotlist': plotlist, 
    'timlist': timlist,
    'leadlist': leadlist,
    'leadlist_link': leadlist_link,
    'fclist': fclist, 
    'initplot': plotlist[0],
    'date_begin': date_fc,
    'date_init': date_fc,
    'plotdir': '/plots',
    'display_details': False,
}

f = codecs.open(filepath, mode='w', encoding='utf-8')
f.write(t.render(**c))
f.close()

# the end
