#!/usr/bin/env python
# -*- encoding: utf-8

from settings_common import conf, proj, cm


# General settings
# ================

conf.datapath.insert(1, '/Data/gfi/metno/thredds/arome25')

# Set the default output location (e.g. for plots)
conf.plotpath = '/Data/gfi/metno/visualisation/web/plots'


# Variable definitions
# ====================

msl = ('msl', 'msl', 'Mean sea level pressure', 'Pa')
t2m = ('t2m', 'T2', '2 metre temperature', 'K')

# Non-dynlib derived variables
ff10 = ('ff10', 'ff10', '10 metre wind speed', 'm s**-1')
trr = ('trr', 'trr', 'Total rain rate', 'm h**-1')

# 1. Surface variables
conf.sfclevs = ['sfc', ]
conf.register_variable([msl, t2m, ff10, trr], conf.sfclevs)



def map_tmp():
	return proj.Basemap(projection='lcc', lat_0=60, lat_ts=60, lon_0=15, resolution='h', 
			llcrnrlon=0.5, llcrnrlat=56.5, urcrnrlon=11, urcrnrlat=63.5)
proj.SNorwaymap = map_tmp


def map_tmp():
	return proj.Basemap(projection='lcc', lat_0=63, lat_ts=63, lon_0=15, resolution='h', 
			llcrnrlon=2.0, llcrnrlat=52.5, urcrnrlon=41.5, urcrnrlat=72.0)
proj.Scandimap = map_tmp


##
# Local settings.

conf.plotf[None,'msl','hook'] = lambda msl: msl/1.0e2
conf.plot[None,'msl','hook'] = lambda msl: msl/1.0e2
conf.plotf[None,'t2m','hook'] = lambda t: t - 273.15
conf.plot[None,'t2m','hook'] = lambda t: t - 273.15
conf.plotf[None,'trr','hook'] = lambda trr: trr + 1.0e-100
conf.plot[None,'trr','hook'] = lambda trr: trr + 1.0e-100

# that's it
