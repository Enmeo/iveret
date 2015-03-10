#!/usr/bin/env python
# -*- encoding: utf8

from datetime import datetime as dt, timedelta as td

from django.conf import settings
from django.template import Context, loader

# Where to save the weather map; 
# TODO: How to avoid the full path info here? The full path should only be defined once in the calling shell script.
basepath = '/Home/siv22/csp001/work/iveret/vaerkart'
filepath = basepath+'/web/vaerkart_npolar.html'
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
    def __init__(self, name, level, prefix):
        self.name = name
        self.level = level
        self.prefix = prefix

v = variable
varlist = [
    v('Potential vorticity', '300 K', 'pvpt300_wind'),
    v('Potential vorticity', '330 K', 'pvpt330_wind'),
    v('Potential vorticity', '350 K', 'pvpt350_wind'),
    v('Potential temperature', 'PV 2', 'ptpv2_wind'),
    v('Total column water vapour', '', 'tcwv'),
]

plotdomains = [
	('ECMWF forecasts North Atlantic', 'vaerkart.html'), 
	('ECMWF forecasts Northern Hemisphere', 'vaerkart_npolar.html'),
	('AROME forecasts Southern Norway', 'vaerkart_arome.html'),
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
	'plot_domains': plotdomains,
	'plot_domain': plotdomains[1][0],
	'plot_prefix': 'ec_for',
	'varlist': varlist, 
	'timlist': timlist,
	'timlist_link': timlist_link,
	'fclist': fclist, 
	'initvar': varlist[0],
	'date_begin': date_fc,
	'date_init': date_fc,
	'plotdir': 'plots_npolar',
})

f = file(filepath, 'w')
f.write(t.render(c))
f.close()

# the end
