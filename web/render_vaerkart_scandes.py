#!/usr/bin/env python
# -*- encoding: utf8

from __future__ import print_function, absolute_import, division, unicode_literals

import codecs
from jinja2 import FileSystemLoader, Environment
from datetime import datetime as dt, timedelta as td

from settings.common import conf, basepath
from current_fc import *
from plotdomains import plotdomains



# Where to save the weather map; 
filepath = conf.plotpath+'/../closed/vaerkart_ec_scandes.html'

env = Environment(loader=FileSystemLoader(searchpath=basepath+'/web'))


date_base = get_current_plotted_fc()
# Override
#date_base = dt(2015,6,9,12)

print('Creating page for forecasts from %s.' % date_base.strftime('%d.%m.%Y, %H UTC'))




# TODO: How to avoid the repetition among the different render_vaerkart*.py scripts?
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
sst = variable(u'Sea surface temperature', '°C', u'')
tshff = variable(u'Total surface heat flux', u'W/m²', u'')

msl = variable(u'Sea level pressure', 'hPa', u'')
barbs10 = variable(u'10 m Wind barbs', u'm/s', u'')

o = overlay
plotlist = [
	plot(u't2m_msl', t2, [o('black dashes', t2, [0,]), o('black', msl, 2)],
		name='2m Temperature and SLP'),
	plot(u'rh2m_tp', tp, [o('grey shading', rh2, [20, 40, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 99]), ], 
		name='2m Relative humidity and precipitation'),
	plot(u'shf_winds', tshff, [o('grey', sst, 1), o('yellow, orange, red', ff10, [17.2, 24.5, 32.7] )], 
		name='Surface fluxes, 10m winds and SSTs'),
]

fclist = [date_base - td(0.5)*i for i in range(11)]
date_fc = fclist[0]

leadlist = list(range(0,73,3))

leadlist_link = range(0,73,6)

timlist = [date_fc + td(0,3600*lead) for lead in leadlist]


# Rendering
t = env.get_template('template_jinja.html')
c = {
	'plot_domains': plotdomains,
	'plot_domain': plotdomains[6][0],
	'plot_prefix': 'ec_for_scandes',
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

f = codecs.open(filepath, 'w', encoding='utf-8')
f.write(t.render(**c))
f.close()

# the end
