#!/usr/bin/env python
# -*- encoding: utf-8

import numpy as np

from dynlib.shorthands import conf, cm, proj
from dynlib.plotsettings.default import pconf, pconfl


# Set the default output location (e.g. for plots)
plotpath = '/share/web/plots'
basepath = '/home/ubuntu/sw/vaerkart'


pconf[None, None, 'cb_orientation'] = 'vertical'
pconf[None,None,'plotpath'] = plotpath
pconf[None,None,'orocolor'] = None
pconf[None,None,'meridians'] = np.arange(-180,180,60)
pconf[None,None,'parallels'] = np.arange(-60,61,30)

pconfl[None,None,'linewidths'] = [1,]

pconf[None,'Geopotential','cmap'] = cm.KPiRdYl1
pconf[None,'Potential vorticity','cmap'] = cm.WYlRd
pconf[None,'Deformation','cmap'] = cm.defabs
pconf[None,'Wind speed','cmap'] = cm.WYlGn
pconf[None,'10m Wind speed','cmap'] = cm.WYlGn

pconf[None,'Temperature','cmap'] = cm.RdYlCyBu2
pconf[None,'2m Temperature','cmap'] = cm.RdYlCyBu2
pconf[None,'Sea surface temperature','cmap'] = cm.RdYlCyBu2
pconf[None,'Temperature anomaly','cmap'] = cm.RdYlCyBu2
pconf[None,'Potential temperature','cmap'] = cm.RdYlCyBu2
pconf[None,'Equivalent potential temperature','cmap'] = cm.RdYlCyBu2

pconf[None,'Specific humidity','cmap'] = cm.WYlBuKPi
pconf[None,'Total column water vapour','cmap'] = cm.WYlBuKPi
pconf[None,'Total column water vapour anomaly','cmap'] = cm.RdYlCyBu2
pconf[None,'Total precipitation','cmap'] = cm.WBuPi2

pconf[None,'Low cloud cover','cmap'] = cm.KBu
pconf[None,'Mid-level cloud cover','cmap'] = cm.KOr
pconf[None,'High cloud cover','cmap'] = cm.gray

pconf [None,'Temperature','hook'] = lambda t: t - 273.15
pconfl[None,'Temperature','hook'] = lambda t: t - 273.15
pconf [None,'2m Temperature','hook'] = lambda t: t - 273.15
pconfl[None,'2m Temperature','hook'] = lambda t: t - 273.15
pconf [None,'Sea-surface temperature','hook'] = lambda t: t - 273.15
pconfl[None,'Sea-surface temperature','hook'] = lambda t: t - 273.15

pconf [None,'Specific humidity','hook'] = lambda q: q*1.0e3
pconfl[None,'Specific humidity','hook'] = lambda q: q*1.0e3

pconf [None,'Sea-level pressure','hook'] = lambda msl: msl/1.0e2
pconfl[None,'Sea-level pressure','hook'] = lambda msl: msl/1.0e2
pconfl[None,'Sea-level pressure','alpha'] = 0.8
pconf [None,'Total precipitation','hook'] = lambda trr: trr + 1.0e-100
pconfl[None,'Total precipitation','hook'] = lambda trr: trr + 1.0e-100

pconfl[None, 'perc', 'scale'] = [0.5, 1.5, 3.5, 15.5, 17.5, 18.5, ]
pconfl[None, 'perc', 'linewidths'] = 1.5

# the end
