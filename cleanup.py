#!/usr/bin/env python

import os
from datetime import datetime as dt, timedelta as td


retain_plots = [
    ('ec','natl','z500_msl'),
    ('ec','natl','t850_msl'),
    ('ec','natl','tcwv'),
    ('ec','natl','iwvt_axis'),
    ('ec','natl','ptpv2_jets'),
    ('ec','npolar','z500_msl'),
    ('ec','npolar','t850_msl'),
    ('ec','npolar','tcwv'),
    ('ec','npolar','ptpv2_jets'),
]

plotdir = '/share/web/plots'



if __name__ == '__main__':
    for path, dirs, files in os.walk(plotdir):
        lst = path.rfind('/')
        sndlst = path.rfind('/', 0, lst)
        trdlst = path.rfind('/', 0, sndlst)

        fcsrc = path[lst+1:]
        plotname = path[sndlst+1:lst]
        domain = path[trdlst+1:sndlst]

        for fname in files:
            pos_for = fname.rfind('_for_')

            # Keep non-matching files
            if pos_for < 0:
                continue

            fromstr = fname[:10]
            forstr = fname[pos_for+5:pos_for+15]

            fromdate = dt.strptime(fromstr, '%Y%m%d%H')

            # Keep current forecasts
            if dt.now() - fromdate < td(10.0):
                continue

            # Keep files in archive
            if (fcsrc,domain,plotname) in retain_plots and fromstr == forstr:
                continue

            # Remove remaining files
            os.remove(f'{path}/{fname}')


# C'est le fin
