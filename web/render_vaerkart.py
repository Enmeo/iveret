#!/usr/bin/env python
# -*- encoding: utf8

import codecs

from datetime import datetime as dt, timedelta as td

from django.conf import settings
from django.template import Context, loader

# Where to save the weather map; 
# TODO: How to avoid the full path info here? The full path should only be defined once in the calling shell script.
filepath = '/Data/gfi/metno/visualisation/web/vaerkart.html'
settings.configure(TEMPLATE_DIRS = ('/Data/gfi/users/csp001/forecasts/web', ))


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


plotlist = [
	plot(u'z500_msl', z500, [('white', z500, 16), ('black', msl, 5)]), 
	plot(u't850_msl', t850, [('black dashes', t850, [0,]), ('black', msl, 5)]),
	plot(u'the850_wind', the850, [('black', barbs850, None), ]),
	plot(u'q850_wind', q850, [('black', barbs850, None), ]),
	plot(u'ff850_wind', ff850, [('black', barbs850, None), ]),
	plot(u'deform850_msl', def850, [('black double-arrows', defang850, None), ('blue', msl, 10), ]),
	plot(u'ff10_wind', ff10, [('black', barbs10, None), ]),
	plot(u'tcwv', tcwv, [('black arrows', icwvt, None), ('magenta', lp, [0.5,1,2]), ('cyan', cp, [0.5,1,2]), ]),
	plot(u'tcc', tcc),
	plot(u'tp', tp),
	plot(u'pvpt300_wind', pvpt300, [('black', barbspt300, None), ]),
	plot(u'pvpt315_wind', pvpt315, [('black', barbspt315, None), ]),
	plot(u'pvpt330_wind', pvpt330, [('black', barbspt330, None), ]),
	plot(u'pvpt350_wind', pvpt350, [('black', barbspt350, None), ]),
	plot(u'ptpv2_wind', ptpv2, [('black', barbspv2, None), ]),
	plot(u'ffpv2_wind', ffpv2, [('black', barbspv2, None), ('white', jetaxespv2, None), ], name='Jets on PV 2'),
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
	'plotlist': plotlist, 
	'timlist': timlist,
	'leadlist': leadlist,
	'leadlist_link': leadlist_link,
	'fclist': fclist, 
	'initplot': plotlist[0],
	'date_begin': date_fc,
	'date_init': date_fc,
	'plotdir': 'plots',
	'display_overlay_details': False,
})

f = codecs.open(filepath, mode='w', encoding='utf-8')
f.write(t.render(c))
f.close()

# the end
