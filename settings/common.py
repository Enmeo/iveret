#!/usr/bin/env python
# -*- encoding: utf-8

from __future__ import print_function, absolute_import, division, unicode_literals

import matplotlib as mpl

from dynlib.settings import conf, cm, proj
import dynlib.context.plot

from . import cb

# Set the default output location (e.g. for plots)
conf.plotpath = '/data/sci/devel/prj/iveret/web/plots'

cm.z = cb.KPiRdYl1
cm.q = cb.WYlBuKPi
cm.pv = cb.WYlRd
cm.t = cb.RdYlCyBu2
cm.ff = cb.WYlGn
cm.lcc = cb.KBu
cm.mcc = cb.KOr
cm.hcc = cm.gray
cm.trr = cb.WBuPi2



def map_tmp():
	return proj.Basemap(projection='lcc', lat_0=60, lat_ts=60, lon_0=15, resolution='h', 
			llcrnrlon=0.5, llcrnrlat=56.5, urcrnrlon=11, urcrnrlat=63.5)
proj.SNorwaymap = map_tmp


def map_tmp():
	return proj.Basemap(projection='lcc', lat_0=63, lat_ts=63, lon_0=15, resolution='h', 
			llcrnrlon=2.0, llcrnrlat=52.5, urcrnrlon=41.5, urcrnrlat=72.0)
proj.Scandimap = map_tmp

def map_tmp():
	return proj.Basemap(projection='lcc', lat_0=77.5, lat_ts=77.5, lon_0=-25, resolution='h', 
			llcrnrlon=-16.0, llcrnrlat=69.5, urcrnrlon=67.5, urcrnrlat=71.5)
proj.AromeArcticMap = map_tmp


# the end
