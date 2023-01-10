#!/usr/bin/env python
# -*- encoding: utf-8

from datetime import datetime as dt, timedelta as td


DATEFMT = '%Y%m%d%H'
STATFILE = '/home/ubuntu/log/status/ecmwf_ext'

def get_current_fc():
    now = dt.now()

    dayhr = now.weekday(), now.hour
    
    # Monday before the first extended range forecast of the week -> most recent is Thursday of previous week
    if dayhr < (0, 20):
        forecast = dt(now.year,now.month,now.day,0) - td(4)
    # Before the second extended range forecast of the week -> most recent is Monday of current week
    elif dayhr < (3, 20): 
        forecast = dt(now.year,now.month,now.day,0) - td(dayhr[0])
    # After second extended range forecast of the week -> most recent is previous Thurday of current week
    else:
        forecast = dt(now.year,now.month,now.day,0) - td(dayhr[0] - 3)

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
