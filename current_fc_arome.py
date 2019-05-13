#!/usr/bin/env python
# -*- encoding: utf-8

from datetime import datetime as dt


DATEFMT = '%Y%m%dT%HZ'
STATFILE = '/home/ubuntu/log/status/arome'

def get_current_fc_arome():
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

	return forecast

def get_current_plotted_fc_arome():
	f = open(STATFILE, 'r')
	datestr = f.read()
	f.close()
	
	return dt.strptime(datestr[:-1], DATEFMT)

if __name__ == '__main__':
	print(get_current_fc_arome().strftime(DATEFMT))

# C'est le fin
