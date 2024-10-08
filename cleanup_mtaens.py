#!/usr/bin/env python

import os
from datetime import datetime as dt, timedelta as td


retain_weekly_inits = [
    (0, 0), # Mondays, 00Z
]


datadirs = [
    '/share/web/mtaens',
    '/share/web/jetens',
]



if __name__ == '__main__':
    now = dt.now()

    for datadir in datadirs:
        for path, dirs, files in os.walk(datadir):
            for fname in sorted(files):
                lst = fname.find('.')
                sndlst = fname.find('.', lst+1)
                trdlst = fname.find('.', sndlst+1)

                datestr = fname[sndlst+1:trdlst]
                date = dt.strptime(datestr, '%Y%m%d%H')
                
                # Keep current data
                if now - date < td(11):
                    continue
                
                # Keep specified weekly initialisations
                if (date.weekday(), date.hour) in retain_weekly_inits:
                    continue

                # Remove remaining files
                os.remove(f'{path}/{fname}')


# C'est le fin
