#!/usr/bin/env python
# -*- encoding: utf-8

from __future__ import print_function, absolute_import, division, unicode_literals

import matplotlib as mpl

from dynlib.settings import cm, proj
from dynlib.settings_basic import conf
import dynlib.context.plot

from . import cb

# Set the default output location (e.g. for plots)
conf.plotpath = '/share/web/plots'
basepath = '/home/ubuntu/sw/vaerkart'

cm.z = cb.KPiRdYl1
cm.q = cb.WYlBuKPi
cm.pv = cb.WYlRd
cm.t = cb.RdYlCyBu2
cm.ff = cb.WYlGn
cm.lcc = cb.KBu
cm.mcc = cb.KOr
cm.hcc = cm.gray
cm.trr = cb.WBuPi2



# Bergen and immediate surroundings
def map_tmp():
	return proj.Basemap(projection='lcc', lat_0=60, lat_ts=60, lon_0=15, resolution='h', 
			llcrnrlon=4.75, llcrnrlat=60.1, urcrnrlon=5.8, urcrnrlat=60.8)
proj.Bergenmap = map_tmp

# Approximately Vestland fylke
def map_tmp():
	return proj.Basemap(projection='lcc', lat_0=60, lat_ts=60, lon_0=15, resolution='h', 
			llcrnrlon=2.0, llcrnrlat=58.5, urcrnrlon=7.97, urcrnrlat=62.5)
proj.Vestlandmap = map_tmp

# Southern Norway 
def map_tmp():
	return proj.Basemap(projection='lcc', lat_0=60, lat_ts=60, lon_0=15, resolution='i', 
			llcrnrlon=-1.5, llcrnrlat=55.4, urcrnrlon=13, urcrnrlat=65.0)
proj.SNorwaymap = map_tmp

# Scandinavia, covering about the entire AROME MetCoop domain
def map_tmp():
	return proj.Basemap(projection='lcc', lat_0=63.3, lat_ts=63.3, lon_0=15, resolution='i', 
			llcrnrlon=0.3, llcrnrlat=50.3, urcrnrlon=54.2, urcrnrlat=71.5)
proj.Scandimap = map_tmp

# Barents Sea, covering about the entire AROME Arctic domain
def map_tmp():
	return proj.Basemap(projection='lcc', lat_0=77.5, lat_ts=77.5, lon_0=-25, resolution='i', 
			llcrnrlon=-16.0, llcrnrlat=69.5, urcrnrlon=67.5, urcrnrlat=71.5)
proj.BarentsSeamap = map_tmp

# Lofoten & Lofoten basin discontinued, replaced by Barents Sea.
#def map_tmp():
#	return proj.Basemap(projection='lcc', lat_0=60, lat_ts=60, lon_0=15, resolution='h', 
#			llcrnrlon=11.5, llcrnrlat=67.08, urcrnrlon=18.0, urcrnrlat=69.5)
#proj.Lofotenmap = map_tmp
#
#def map_tmp():
#	return proj.Basemap(projection='lcc', lat_0=60, lat_ts=60, lon_0=15, resolution='h', 
#			llcrnrlon=1.7, llcrnrlat=66.5, urcrnrlon=20, urcrnrlat=71.5)
#proj.LofotenBasinmap = map_tmp


# the end
