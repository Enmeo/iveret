#!/usr/bin/env python
# -*- encoding: utf8

import codecs

from datetime import datetime as dt, timedelta as td

from django.conf import settings
from django.template import Context, loader

# Where to save the weather map; 
# TODO: How to avoid the full path info here? The full path should only be defined once in the calling shell script.
basepath = '/Data/gfi/metno/visualisation'
filepath = basepath+'/web/vaerkart.html'
settings.configure(TEMPLATE_DIRS = (basepath+'/web', ), DEFAULT_CHARSET='utf-8')


# The only free parameter for the entire script
now = dt.now()
if now.hour in range(11,23):
	date_base = dt(now.year,now.month,now.day,0)
else:
	date_base = dt(now.year,now.month,now.day,12)
	if now.hour < 11:
		date_base -= td(1,0)
print 'Creating page for forecasts from %s.' % date_base.strftime('%d.%m.%Y, %H UTC')



# Defining stuff
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
z500 = variable(u'Geopotential', u'gpdm', u'500 hPa')
t850 = variable(u'Temperature', u'°C', u'850 hPa')
the850 = variable(u'Eq. Pot. Temperature', 'K', u'850 hPa')
q850 = variable(u'Spec. Humidity', 'g/kg', u'850 hPa')
ff850 = variable(u'Wind speed', 'm/s', u'850 hPa')
def850 = variable(u'Deformation', '10⁻⁵/s', u'850 hPa')
ff10 = variable(u'10 m wind speed', 'm/s', u'')
tcwv = variable(u'Total column water vapour', 'kg/m²', u'')
tcc = variable(u'Total cloud cover', '', u'')
tp = variable(u'Precipitiation', 'mm/h', u'')
pvpt300 = variable(u'Potential vorticity', 'PVU', u'300 K')
pvpt315 = variable(u'Potential vorticity', 'PVU', u'315 K')
pvpt330 = variable(u'Potential vorticity', 'PVU', u'330 K')
pvpt350 = variable(u'Potential vorticity', 'PVU', u'350 K')
ptpv2 = variable(u'Potential temperature', 'K', u'PV 2')
ffpv2 = variable(u'Wind speed', 'm/s', u'PV 2')

msl = variable(u'Sea level pressure', 'hPa', u'')
cp = variable(u'Convective precipitation', 'mm/h', u'')
lp = variable(u'Large-scale precipitation', 'mm/h', u'')
barbs850 = variable(u'Wind barbs', u'm/s', u'850 hPa')
barbs10 = variable(u'10 m Wind barbs', u'm/s', u'')
barbspt300 = variable(u'Wind barbs', u'm/s', u'300 K')
barbspt315 = variable(u'Wind barbs', u'm/s', u'315 K')
barbspt330 = variable(u'Wind barbs', u'm/s', u'330 K')
barbspt350 = variable(u'Wind barbs', u'm/s', u'350 K')
barbspv2 = variable(u'Wind barbs', u'm/s', u'PV 2')
defang850 = variable(u'Axes of dilatation', u'', u'850 hPa')
icwvt = variable(u'Integrated column water vapour transport', u'', u'')
jetaxespv2 = variable(u'Jet axes', u'', u'PV 2')

o = overlay
plotlist = [
	plot(u'z500_msl', z500, [o('white', z500, 16), o('black', msl, 5)], 
		name='500 hPa Geopotential and SLP'), 
	plot(u't850_msl', t850, [o('black dashes', t850, [0,]), o('black', msl, 5)],
		name='850 hPa Temperature and SLP'),
	plot(u'the850_wind', the850, [o('black', barbs850, None), ],
		name='850 hPa Equiv. pot. temperature and winds'),
	plot(u'q850_wind', q850, [o('black', barbs850, None), o('magenta', lp, [1,3,10]), o('cyan', cp, [1,3,10]), ],
		name='850 hPa Spec. humidity, precipitation and winds'),
	plot(u'ff850_wind', ff850, [o('black', barbs850, None), ],
		name='850 hPa Wind speed and direction'),
	plot(u'deform850_msl', def850, [o('black double-arrows', defang850, None), o('blue', msl, 10), ],
		name='850 hPa Horizontal deformation and SLP'),
	plot(u'ff10_wind', ff10, [o('black', barbs10, None), ],
		name='10 m Wind speed and direction'),
	plot(u'tcwv', tcwv, [o('black arrows', icwvt, None), o('magenta', lp, [1,3,10]), o('cyan', cp, [1,3,10]), ],
		name='Total column water vapour, integrated fluxes and precipitation'),
	plot(u'tcc', tcc),
	plot(u'tp', tp),
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
]

plotdomains = [
	('ECMWF forecasts North Atlantic', 'vaerkart.html'), 
	('ECMWF forecasts Northern Hemisphere', 'vaerkart_npolar.html'),
	('AROME forecasts Southern Norway', 'vaerkart_arome.html'),
]

fclist = [date_base - td(0.5)*i for i in range(11)]
date_fc = fclist[0]

leadlist = range(0,144,3)
leadlist.extend(range(144,241,6))

leadlist_link = range(0,241,12)

timlist = [date_fc + td(0,3600*lead) for lead in leadlist]


# Rendering

t = loader.get_template(template_name='template.html')
c = Context({
	'plot_domains': plotdomains,
	'plot_domain': plotdomains[0][0],
	'plot_prefix': 'ec_for',
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
