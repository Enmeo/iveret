#!/usr/bin/env python
# -*- encoding: utf8

from __future__ import print_function, absolute_import, division, unicode_literals

import codecs

from datetime import datetime as dt, timedelta as td

from settings.common import conf

from jinja2 import FileSystemLoader, Environment


# Where to save the weather map; 
filepath = conf.plotpath+'/../vaerkart_arome_arctic.html'

env = Environment(loader=FileSystemLoader(searchpath=conf.plotpath+'/..'))


# The only free parameter for the entire script
now = dt.now()
if now.hour in range(5,11):
	date_base = dt(now.year,now.month,now.day,0)
elif now.hour in range(11,17):
	date_base = dt(now.year,now.month,now.day,6)
elif now.hour in range(17,23):
	date_base = dt(now.year,now.month,now.day,12)
else:
	date_base = dt(now.year,now.month,now.day,18)
	if now.hour < 5:
		date_base -= td(1,0)

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
sic = variable(u'Sea ice concentration', '', u'')
sst = variable(u'Sea surface temperature', '°C', u'')
tshff = variable(u'Total Surface heat flux', u'W/m²', u'')
#slhff = variable(u'Surface latent heat flux', u'W/m²', u'')

msl = variable(u'Sea level pressure', 'hPa', u'')
barbs10 = variable(u'10 m Wind barbs', u'm/s', u'')

o = overlay
plotlist = [
	plot(u't2m_msl', t2, [o('black dashes', t2, [0,]), o('black', msl, 2)],
		name='2m Temperature and SLP'),
	plot(u'rh2m_tp', tp, [o('grey shading', rh2, [20, 40, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 99]), o('pale red', sic, [0.2, 0.8] )], 
		name='2m Relative humidity, precipitation and MIZ'),
	plot(u'shf_winds', tshff, [o('grey', sst, 1), o('light blue', sic, [0.2, 0.8] ), o('yellow, orange, red', ff10, [17.2, 24.5, 32.7] )], 
		name='Surface fluxes, 10m winds and SSTs, MIZ and dangerous winds'),
]

plotdomains = [
	('ECMWF forecasts North Atlantic', 'vaerkart.html'), 
	('ECMWF forecasts Northern Hemisphere', 'vaerkart_npolar.html'),
	('ECMWF forecasts Southern Hemisphere', 'vaerkart_spolar.html'),
	('AROME forecasts Southern Norway', 'vaerkart_arome.html'),
	('AROME forecasts Scandinavia', 'vaerkart_arome_scandies.html'),
	('AROME Arctic forecasts', 'vaerkart_arome_arctic.html'),
]

fclist = [date_base - td(0.25)*i for i in range(11)]
date_fc = fclist[0]

leadlist = range(0,67,3)
leadlist_link = range(0,67,6)

timlist = [date_fc + td(0,3600*lead) for lead in leadlist]


# Rendering
t = env.get_template('template_jinja.html')
c = { 
	'plot_domains': plotdomains,
	'plot_domain': plotdomains[5][0],
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
