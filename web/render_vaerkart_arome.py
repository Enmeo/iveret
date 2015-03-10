#!/usr/bin/env python
# -*- encoding: utf8

import codecs

from datetime import datetime as dt, timedelta as td

from django.conf import settings
from django.template import Context, loader

# Where to save the weather map; 
# TODO: How to avoid the full path info here? The full path should only be defined once in the calling shell script.
basepath = '/Home/siv22/csp001/work/iveret/vaerkart'
filepath = basepath+'/web/vaerkart_arome.html'
settings.configure(TEMPLATE_DIRS = (basepath+'/web', ), DEFAULT_CHARSET='utf-8')


# The only free parameter for the entire script
now = dt.now()
if now.hour in range(4,10):
	date_base = dt(now.year,now.month,now.day,0)
elif now.hour in range(10,16):
	date_base = dt(now.year,now.month,now.day,6)
elif now.hour in range(16,22):
	date_base = dt(now.year,now.month,now.day,12)
else:
	date_base = dt(now.year,now.month,now.day,18)
	if now.hour < 11:
		date_base -= td(1,0)

# Override 
#date_base = dt(2015,2,3,0)

print 'Creating page for forecasts from %s.' % date_base.strftime('%d.%m.%Y, %H UTC')



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
tp = variable(u'Precipitiation', 'mm/?', u'')

msl = variable(u'Sea level pressure', 'hPa', u'')
barbs10 = variable(u'10 m Wind barbs', u'm/s', u'')

o = overlay
plotlist = [
	plot(u't2m_msl', t2, [o('black dashes', t2, [0,]), o('black', msl, 2)],
		name='2m Temperature and SLP'),
	plot(u'ff10_wind', ff10, [o('black', barbs10, None), ],
		name='10 m Wind speed and direction'),
	plot(u'tp', tp),
]

plotdomains = [
	('ECMWF forecasts North Atlantic', 'vaerkart.html'), 
	('ECMWF forecasts Northern Hemisphere', 'vaerkart_npolar.html'),
	('AROME forecasts Southern Norway', 'vaerkart_arome.html'),
	('AROME forecasts Scandinavia', 'vaerkart_arome_scandies.html'),
]

fclist = [date_base - td(0.25)*i for i in range(11)]
date_fc = fclist[0]

leadlist = range(0,67,3)
leadlist_link = range(0,67,6)

timlist = [date_fc + td(0,3600*lead) for lead in leadlist]


# Rendering
t = loader.get_template(template_name='template.html')
c = Context({
	'plot_domains': plotdomains,
	'plot_domain': plotdomains[2][0],
	'plot_prefix': 'no_for',
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
})

f = codecs.open(filepath, mode='w', encoding='utf-8')
f.write(t.render(c))
f.close()

# the end
