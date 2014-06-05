#!/usr/bin/env python
# -*- encoding: utf8

from datetime import datetime as dt, timedelta as td

from django.conf import settings
from django.template import Context, loader

settings.configure(TEMPLATE_DIRS = ('/data/devel/vaerkart', ))


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
    def __init__(self, name, level, prefix):
        self.name = name
        self.level = level
        self.prefix = prefix

v = variable
varlist = [
    v('Geopotential', '500 hPa', 'z500_msl'), 
    v('Temperature', '850 hPa', 't850_msl'),
    v('Spec. Humidity', '850 hPa', 'q850_wind'),
    v('Total column water vapour', '', 'tcwv'),
    v('Total cloud cover', '', 'tcc'),
    v('Precipitiation', '', 'tp'),
    v('Potential vorticity', '300 K', 'pvpt300_wind'),
    v('Potential vorticity', '330 K', 'pvpt330_wind'),
    v('Potential vorticity', '350 K', 'pvpt350_wind'),
    v('Potential temperature', 'PV 2', 'ptpv2_wind'),
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
})

f = file('vaerkart.html', 'w')
f.write(t.render(c))
f.close()

# the end
