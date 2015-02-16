#!/usr/bin/env python
# -*- encoding: utf8

import codecs

from datetime import datetime as dt, timedelta as td

from django.conf import settings
from django.template import Context, loader

# Where to save the weather map; 
# TODO: How to avoid the full path info here? The full path should only be defined once in the calling shell script.
basepath = '/Home/siv22/csp001/work/iveret/vaerkart'
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
# Override
date_base = dt(2015,2,3,0)
print 'Creating page for forecasts from %s.' % date_base.strftime('%d.%m.%Y, %H UTC')



# Defining stuff
class variable(object):
    def __init__(self, name, level, prefix):
        self.name = name
        self.level = level
        self.prefix = prefix

v = variable
varlist = [
    v(u'Geopotential [gpdm]', u'500 hPa', u'z500_msl'), 
    v(u'Temperature [°C]', u'850 hPa', u't850_msl'),
    v(u'Eq. Pot. Temperature [K]', u'850 hPa', u'the850_wind'),
    v(u'Spec. Humidity [g/kg]', u'850 hPa', u'q850_wind'),
    v(u'Wind speed [m/s]', u'850 hPa', u'ff850_wind'),
    v(u'Deformation [10⁻⁵/s]', u'850 hPa', u'deform850_msl'),
    v(u'10m wind speed [m/s]', u'', u'ff10_wind'),
    v(u'Total column water vapour [kg/m²]', u'', u'tcwv'),
    v(u'Total cloud cover [%]', u'', u'tcc'),
    v(u'Precipitiation [mm/h]', u'', u'tp'),
    v(u'Potential vorticity [PVU]', u'300 K', u'pvpt300_wind'),
    v(u'Potential vorticity [PVU]', u'330 K', u'pvpt330_wind'),
    v(u'Potential vorticity [PVU]', u'350 K', u'pvpt350_wind'),
    v(u'Potential temperature [K]', u'PV 2', u'ptpv2_wind'),
    v(u'Wind speed [m/s], jets axes', u'PV 2', u'ffpv2_wind'),
]

fclist = [date_base - td(0.5)*i for i in range(11)]
date_fc = fclist[0]

timlist = [date_base + td(0.125)*i for i in range(48)]
timlist.extend([date_base + td(6) + td(0.25)*i for i in range(17)])

timlist_link = [date_base + td(0.5)*i for i in range(21)]
timlist_link = map(lambda d: (d, int((d-date_fc).total_seconds()/3600)), timlist_link)


# Rendering

t = loader.get_template(template_name='template.html')
c = Context({
    'varlist': varlist, 
    'timlist': timlist,
    'timlist_link': timlist_link,
    'fclist': fclist, 
    'initvar': varlist[0],
    'date_begin': date_fc,
    'date_init': date_fc,
    'plotdir': 'plots',
})

f = codecs.open(filepath, mode='w', encoding='utf-8')
f.write(t.render(c))
f.close()

# the end
