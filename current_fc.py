#!/usr/bin/env python
# -*- encoding: utf-8

from datetime import datetime as dt, timedelta as td


DATEFMT = '%Y%m%d%H'
STATFILE = '/home/ubuntu/log/status/ecmwf'

def get_current_fc():
	now = dt.now()

	if now.hour in range(7,19):
		forecast = dt(now.year,now.month,now.day,0)
	else:
		forecast = dt(now.year,now.month,now.day,12)
		if now.hour < 7:
			forecast -= td(1,0)
	
	# Override
	#forecast = dt(2018,10,14,12)
	
	return forecast

def get_current_plotted_fc():
	f = open(STATFILE, 'r')
	datestr = f.read()
	f.close()
	
	return dt.strptime(datestr[:-1], DATEFMT)

if __name__ == '__main__':
	print(get_current_fc().strftime(DATEFMT))

# C'est le fin
