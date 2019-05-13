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
filepath = conf.plotpath+'/../closed/vaerkart_ec_spolar.html'

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
z500 = variable(u'Geopotential', u'gpdm', u'500 hPa')
tcwv = variable(u'Total column water vapour', 'kg/m²', u'')
pvpt315 = variable(u'Potential vorticity', 'PVU', u'315 K')
pvpt330 = variable(u'Potential vorticity', 'PVU', u'330 K')
ptpv2 = variable(u'Potential temperature', 'K', u'PV 2')

msl = variable(u'Sea level pressure', 'hPa', u'')
t850 = variable(u'Temperature', u'°C', u'850 hPa')
cp = variable(u'Convective precipitation', 'mm/h', u'')
lp = variable(u'Large-scale precipitation', 'mm/h', u'')
irbarbspt315 = variable(u'Irrot. wind barbs', u'm/s', u'315 K')
irbarbspt330 = variable(u'Irrot. wind barbs', u'm/s', u'330 K')
icwvt = variable(u'Integrated column water vapour transport', u'', u'')
ffpv2 = variable(u'Wind speed', 'm/s', u'PV 2')
jetaxespv2 = variable(u'Jet axes', u'', u'PV 2')

o = overlay
plotlist = [
	plot(u'z500_msl', z500, [o('white', z500, [552,]), o('black', msl, 5)], 
		name='500 hPa Geopotential and SLP'), 
	plot(u'tcwv', tcwv, [o('black arrows', icwvt, None), 
		o('magenta', lp, [1,3,10]), o('cyan', cp, [1,3,10]), o('dark red', t850, [-5,]), ],
		name='Total column water vapour, integrated fluxes and precipitation'),
	plot(u'ptpv2_jets', ptpv2, [o('black', ffpv2, [30, 45, 60, 75, 90]), o('white', jetaxespv2, None)],
		name='PV2 Pot. temperature, jets and wind speed'),
	plot(u'pvpt315_irot_wind', pvpt315, [o('black', irbarbspt315, None), ],
		name='315 K Pot. Vorticity and irrot. winds'),
	plot(u'pvpt330_irot_wind', pvpt330, [o('black', irbarbspt330, None), ],
		name='330 K Pot. Vorticity and irrot. winds'),
]

fclist = [date_base - td(0.5)*i for i in range(11)]
date_fc = fclist[0]

leadlist = list(range(0,72,3))
leadlist.extend(range(72,241,6))

leadlist_link = range(0,241,12)

timlist = [date_fc + td(0,3600*lead) for lead in leadlist]


# Rendering
t = env.get_template('template_jinja.html')
c = {
	'plot_domains': plotdomains,
	'plot_domain': plotdomains[5][0],
	'plot_prefix': 'ec_for_spolar',
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
