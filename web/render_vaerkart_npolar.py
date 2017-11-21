#!/usr/bin/env python
# -*- encoding: utf8

from __future__ import print_function, absolute_import, division, unicode_literals

import codecs

from datetime import datetime as dt, timedelta as td

from settings.common import conf

import django
from django.conf import settings
from django.template import Context, loader

# Where to save the weather map; 
filepath = conf.plotpath+'/../vaerkart_npolar.html'
settings.configure(
	TEMPLATES=[{
		'DIRS': [conf.plotpath+'/..', ],
		'BACKEND': 'django.template.backends.django.DjangoTemplates',
	}, ], 
	DEFAULT_CHARSET='utf-8'
)
django.setup()


# The only free parameter for the entire script
now = dt.now()
if now.hour in range(11,23):
	date_base = dt(now.year,now.month,now.day,0)
else:
	date_base = dt(now.year,now.month,now.day,12)
	if now.hour < 11:
		date_base -= td(1,0)

# Override
#date_base = dt(2016,10,5,12)

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
tcwv = variable(u'Total column water vapour', 'kg/m²', u'')
pvpt300 = variable(u'Potential vorticity', 'PVU', u'300 K')
ffpt300 = variable(u'Wind speed', 'm/s', u'300 K')
pvpt315 = variable(u'Potential vorticity', 'PVU', u'315 K')
ffpt315 = variable(u'Wind speed', 'm/s', u'315 K')
pvpt330 = variable(u'Potential vorticity', 'PVU', u'330 K')
ffpt330 = variable(u'Wind speed', 'm/s', u'330 K')
pvpt350 = variable(u'Potential vorticity', 'PVU', u'350 K')
ffpt350 = variable(u'Wind speed', 'm/s', u'350 K')
ptpv2 = variable(u'Potential temperature', 'K', u'PV 2')
ffpv2 = variable(u'Wind speed', 'm/s', u'PV 2')

cp = variable(u'Convective precipitation', 'mm/h', u'')
lp = variable(u'Large-scale precipitation', 'mm/h', u'')
barbspt300 = variable(u'Wind barbs', u'm/s', u'300 K')
barbspt315 = variable(u'Wind barbs', u'm/s', u'315 K')
barbspt330 = variable(u'Wind barbs', u'm/s', u'330 K')
barbspt350 = variable(u'Wind barbs', u'm/s', u'350 K')
barbspv2 = variable(u'Wind barbs', u'm/s', u'PV 2')
icwvt = variable(u'Integrated column water vapour transport', u'', u'')
jetaxespv2 = variable(u'Jet axes', u'', u'PV 2')

o = overlay
plotlist = [
	plot(u'pvpt300_wind', pvpt300, [o('black', barbspt300, None), ],
		name='300 K Pot. Vorticity and winds'),
	plot(u'pvpt315_wind', pvpt315, [o('black', barbspt315, None), ],
		name='315 K Pot. Vorticity and winds'),
	plot(u'pvpt330_wind', pvpt330, [o('black', barbspt330, None), ],
		name='330 K Pot. Vorticity and winds'),
	plot(u'pvpt350_wind', pvpt350, [o('black', barbspt350, None), ],
		name='350 K Pot. Vorticity and winds'),
	plot(u'ptpv2_wind', ptpv2, [o('black', barbspv2, None), ],
		name='PV2 Pot. temperature and winds'),
	plot(u'ffpv2_wind', ffpv2, [o('black', barbspv2, None), o('white', jetaxespv2, None), ],
		name='PV2 Wind speed, direction and jet axes'),
	plot(u'tcwv', tcwv, [o('black arrows', icwvt, None), o('magenta', lp, [1,3,10]), o('cyan', cp, [1,3,10]), ],
		name='Total column water vapour, integrated fluxes and precipitation'),
]

plotdomains = [
	('ECMWF forecasts North Atlantic', 'vaerkart.html'), 
	('ECMWF forecasts Northern Hemisphere', 'vaerkart_npolar.html'),
	('ECMWF forecasts Southern Hemisphere', 'vaerkart_spolar.html'),
	('AROME forecasts Southern Norway', 'vaerkart_arome.html'),
	('AROME forecasts Scandinavia', 'vaerkart_arome_scandies.html'),
	('AROME Arctic forecasts', 'vaerkart_arome_arctic.html'),
]

fclist = [date_base - td(0.5)*i for i in range(11)]
date_fc = fclist[0]

leadlist = list(range(0,144,3))
leadlist.extend(range(144,241,6))

leadlist_link = range(0,241,12)

timlist = [date_fc + td(0,3600*lead) for lead in leadlist]


# Rendering
t = loader.get_template(template_name='template.html')
c = Context({
	'plot_domains': plotdomains,
	'plot_domain': plotdomains[1][0],
	'plot_prefix': 'ec_for_npolar',
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

f = codecs.open(filepath, 'w', encoding='utf-8')
f.write(t.render(c))
f.close()

# the end
