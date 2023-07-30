#!/usr/bin/env python
# -*- encoding: utf-8

from datetime import datetime as dt, timedelta as td


DATEFMT = '%Y%m%d%H'
STATFILE = '/home/ubuntu/log/status/ecmwf_ext'

def get_current_fc():
    now = dt.now()
    hr = now.hour
    
    if hr <  20:
        forecast = dt(now.year,now.month,now.day,0) - td(1)
    else:
        forecast = dt(now.year,now.month,now.day,0)

    # Override
    #forecast = dt(2023,1,2,0)
    
    return forecast

def get_current_plotted_fc():
    f = open(STATFILE, 'r')
    datestr = f.read()
    f.close()
    
    return dt.strptime(datestr[:-1], DATEFMT)

if __name__ == '__main__':
    print(get_current_fc().strftime(DATEFMT))

# C'est le fin
