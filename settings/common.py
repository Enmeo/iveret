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

pconf[None,'z','cmap'] = cm.KPiRdYl1
pconf[None,'pv','cmap'] = cm.WYlRd
pconf[None,'defabs','cmap'] = cm.defabs
pconf[None,'ff','cmap'] = cm.WYlGn
pconf[None,'ff10','cmap'] = cm.WYlGn

pconf[None,'t','cmap'] = cm.RdYlCyBu2
pconf[None,'t2m','cmap'] = cm.RdYlCyBu2
pconf[None,'sst','cmap'] = cm.RdYlCyBu2
pconf[None,'t_ano','cmap'] = cm.RdYlCyBu2
pconf[None,'pt','cmap'] = cm.RdYlCyBu2
pconf[None,'eqpt','cmap'] = cm.RdYlCyBu2

pconf[None,'q','cmap'] = cm.WYlBuKPi
pconf[None,'tcwv','cmap'] = cm.WYlBuKPi
pconf[None,'tcwv_ano','cmap'] = cm.RdYlCyBu2
pconf[None,'trr','cmap'] = cm.WBuPi2

pconf[None,'lcc','cmap'] = cm.KBu
pconf[None,'mcc','cmap'] = cm.KOr
pconf[None,'hcc','cmap'] = cm.gray

pconf [None,'t','hook'] = lambda t: t - 273.15
pconfl[None,'t','hook'] = lambda t: t - 273.15
pconf [None,'t2m','hook'] = lambda t: t - 273.15
pconfl[None,'t2m','hook'] = lambda t: t - 273.15
pconf [None,'sst','hook'] = lambda t: t - 273.15
pconfl[None,'sst','hook'] = lambda t: t - 273.15

pconfl[None, 'perc', 'scale'] = [0.5, 1.5, 3.5, 15.5, 17.5, 18.5, ]
pconfl[None, 'perc', 'linewidths'] = 1.5

# the end
