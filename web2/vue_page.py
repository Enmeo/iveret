#!/usr/bin/env python

import codecs
from datetime import datetime as dt, timedelta as td
from jinja2 import FileSystemLoader, Environment

from settings.common import basepath
from current_fc import get_current_plotted_fc as get_ec_initdate
from current_fc_gfs import get_current_plotted_fc_gfs as get_noaa_initdate
from current_fc_arome import get_current_plotted_fc_arome as get_no_initdate

filepath = '/share/web/2.0/index.html'
if __name__ == '__main__':
    today = dt.today()

    ec = get_ec_initdate()
    noaa = get_noaa_initdate()
    no = get_no_initdate()
    no_kyst = dt(today.year, today.month, today.day) - td(1)

    print('Creating Vue page based on')
    print(' - EC forecasts from %s' % ec.strftime('%d.%m.%Y, %H UTC'))
    print(' - NOAA forecasts from %s' % noaa.strftime('%d.%m.%Y, %H UTC'))
    print(' - AROME forecasts from %s' % no.strftime('%d.%m.%Y, %H UTC'))
    print(' - NorKyst/ROMS Nordic forecasts from %s' % no_kyst.strftime('%d.%m.%Y, %H UTC'))

    env = Environment(loader=FileSystemLoader(searchpath=basepath+'/web2'))
    t = env.get_template('template.html')
    c = {'ec': ec, 'noaa': noaa, 'no': no, 'no_kyst': no_kyst, }
    f = codecs.open(filepath, mode='w', encoding='utf-8')
    f.write(t.render(**c))
    f.close()

# C'est le fin
