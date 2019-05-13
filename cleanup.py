#!/usr/bin/env python

import os
from datetime import datetime as dt, timedelta as td


retain_plots = [
	'ec_for_z500_msl', 'ec_for_t850_msl', 'ec_for_tcwv', 
	'ec_for_npolar_ptpv2_wind', 'ec_for_npolar_tcwv',
]

plotdir = '/share/web/plots'



if __name__ == '__main__':
	filenames = os.listdir(plotdir)
	for fname in filenames:
		pos_for = fname.rfind('_for_')
		pos_from = fname.rfind('_from_')

		# Keep non-matching files
		if pos_for < 0 or pos_from < 0:
			continue

		plotname = fname[:pos_from]
		fromstr = fname[pos_from+6:pos_from+16]
		forstr = fname[pos_for+5:pos_for+15]
		
		fromdate = dt.strptime(fromstr, '%Y%m%d%H')

		# Keep current forecasts
		if dt.now() - fromdate < td(7.0):
			continue

		# Keep files in archive
		if plotname in retain_plots and fromstr == forstr:
			continue

		# Remove remaining files
		os.remove(plotdir+'/'+fname)



# C'est le fin
