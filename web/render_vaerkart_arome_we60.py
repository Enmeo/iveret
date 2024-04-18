#!/usr/bin/env python
# -*- encoding: utf8

import codecs
from jinja2 import FileSystemLoader, Environment
from datetime import datetime as dt, timedelta as td

from settings.common import basepath, plotpath
from current_fc_arome import *
from plotdomains import plotdomains


# Where to save the weather map; 
filepath = plotpath+'/../vaerkart_arome_we60.html'

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
eqpt = variable(u'Equivalent potential temperature', u'K', u'')
q = variable(u'Specific humidity', u'g/kg', u'')
eturb = variable(u'Turbulent kinetic energy', u'm²/s²', u'')
cc = variable(u'Cloud cover area fraction', u'', u'')
ff = variable(u'Wind speed', u'm/s', u'')
v = variable(u'Cross-plane winds', u'm/s', u'')
t = variable(u'Temperature', u'°C', u'')
pt = variable(u'Potential temperature', u'K', u'')
quiver = variable(u'Wind vectors', u'', u'')


o = overlay
plotlist = [
    plot(u'ff_pt', v, [o('black', pt, 5), o('thick black', pt, [270, 300, 350, ]), o('vectors', quiver, None), ],
        name='Winds and pot. temperature'),
    plot(u'eqpt_pt', eqpt, [o('red', t, [0, ]), o('black', pt, 5), o('thick black', pt, [270, 300, 350, ])],
        name='Equivalent pot. temperature and pot. temperature'),
    plot(u'q_pt', q, [o('red', t, [0, ]), o('black', pt, 5), o('thick black', pt, [270, 300, 350, ])],
        name='Humidity and pot. temperature'),
#    plot(u'eturb_pt', eturb, [o('black', pt, 5), o('thick black', pt, [270, 300, 350, ])],
#        name='Turbulence and pot. temperature'),
    plot(u'cc_pt', cc, [o('black', pt, 5), o('thick black', pt, [270, 300, 350, ])],
        name='Cloud fraction and pot. temperature'),
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
    'plot_domain': plotdomains[11][0],
    'fcsrc': 'no',
    'domain': 'we60',
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
