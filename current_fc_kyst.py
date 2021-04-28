#!/usr/bin/env python
# -*- encoding: utf-8

from datetime import datetime as dt, timedelta as td


def get_current_fc_kyst():
	''' Return the most recent available forecast init time '''

	now = dt.now()
	if now.hour in range(0,11):
		forecast = dt(now.year,now.month,now.day,0)
		forecast -= td(1,0)
	else:
		forecast = dt(now.year,now.month,now.day,0)

	# Override
	#forecast = dt(2018,10,8,0)

	return forecast


if __name__ == '__main__':
	print(get_current_fc_kyst().strftime('%Y%m%d%H'))

# C'est le fin
