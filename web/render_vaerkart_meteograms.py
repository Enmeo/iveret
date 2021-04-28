#!/usr/bin/env python
# -*- encoding: utf8

import codecs
from jinja2 import FileSystemLoader, Environment
from datetime import datetime as dt, timedelta as td

from settings.common import basepath, plotpath
from current_fc import *
from plotdomains import plotdomains



# Where to save the weather map; 
filepath = plotpath+'/../closed/vaerkart_ec_meteograms.html'

env = Environment(loader=FileSystemLoader(searchpath=basepath+'/web'))

date_base = get_current_plotted_fc()
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
tcwv = variable(u'Total column water vapour', 'kg/m²', u'')
t2 = variable(u'2m Temperature', u'°C', u'')
msl = variable(u'Sea-level pressure', u'hPa', u'')

o = overlay
plotlist = [
    plot(u't2m_bgo', t2, [], name='2m Temperature Bergen'), 
    plot(u't2m_modal_bgo', t2, [], name='Multimodality in 2m temperature Bergen (KMeans)'), 
    plot(u't2m_modal_naive_bgo', t2, [], name='Multimodality in 2m temperature Bergen (Naive)'),
    plot(u'tcwv_bgo', tcwv, [], name='Total column water vapour Bergen'), 
    plot(u'tcwv_modal_bgo', tcwv, [], name='Multimodality in total column water vapour Bergen (KMeans)'), 
    plot(u'tcwv_modal_naive_bgo', tcwv, [], name='Multimodality in total column water vapour Bergen (Naive)'), 
    plot(u'msl_bgo', msl, [], name='Sea-level pressure Bergen'), 
    plot(u'msl_modal_bgo', msl, [], name='Multimodality in sea-level pressure Bergen (KMeans)'), 
    plot(u'msl_modal_naive_bgo', msl, [], name='Multimodality in sea-level pressure Bergen (Naive)'), 
]

fclist = [date_base - td(0.5)*i for i in range(15)]
date_fc = fclist[0]

leadlist = [0, ]
leadlist_link = [0, ]

timlist = [date_fc + td(0,3600*lead) for lead in leadlist]


# Rendering
t = env.get_template('template_jinja_meteograms.html')
c = {
    'plot_domains': plotdomains,
    'plot_domain': plotdomains[7][0],
    'fcsrc': 'ec', 
    'domain': 'meteograms',
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
    'archive': {},
}

f = codecs.open(filepath, mode='w', encoding='utf-8')
f.write(t.render(**c))
f.close()

# the end
