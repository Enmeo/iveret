#!/usr/bin/env python
# -*- encoding: utf-8

from datetime import datetime as dt, timedelta as td


DATEFMT = '%Y-%m-%dT%H:%M:%SZ'
STATFILE = '/home/ubuntu/log/status/gfs'

def get_current_fc_dmi():
    ''' Return the most recent available forecast init time '''

    now = dt.now()
    if now.hour in range(3,9):
        forecast = dt(now.year,now.month,now.day,0)
    elif now.hour in range(9,15):
        forecast = dt(now.year,now.month,now.day,6)
    elif now.hour in range(15,21):
        forecast = dt(now.year,now.month,now.day,12)
    else:
        forecast = dt(now.year,now.month,now.day,18)
        if now.hour < 3:
            forecast -= td(1,0)
    
    # Optional: Override
    #forecast = dt(2019,6,23,0)

    return forecast

def get_current_plotted_fc_dmi():
    f = open(STATFILE, 'r')
    datestr = f.read()
    f.close()
    
    return dt.strptime(datestr[:-1], DATEFMT)

if __name__ == '__main__':
    print(get_current_fc_dmi().strftime(DATEFMT))

# C'est le fin
