#!/usr/bin/env python
# -*- encoding: utf-8

from datetime import datetime as dt


def get_current_fc_gfs():
	''' Return the most recent available forecast init time '''

	now = dt.now()
	if now.hour in range(5,11):
		forecast = dt(now.year,now.month,now.day,0)
	elif now.hour in range(11,17):
		forecast = dt(now.year,now.month,now.day,6)
	elif now.hour in range(17,23):
		forecast = dt(now.year,now.month,now.day,12)
	else:
		forecast = dt(now.year,now.month,now.day,18)
		if now.hour < 5:
			forecast -= td(1,0)

	return forecast


def get_avail_leads():
	''' Return the available lead times '''

	leads = list(range(0,72,3))
	leads += list(range(72,241,6))

	return leads


if __name__ == '__main__':
	print(get_current_fc_gfs().strftime('%Y%m%d%H'))

# C'est le fin
