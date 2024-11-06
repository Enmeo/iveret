#!/usr/bin/env python
# -*- encoding: utf-8

import numpy as np

from dynlib.shorthands import conf, cm, proj
from dynlib.plotsettings.default import pconf, pconfl


# Set the default output location (e.g. for plots)
VAERKART_ROOT = '/home/ubuntu/sw/vaerkart'
conf.datapath.append(VAERKART_ROOT)

WEB_ROOT = '/share/web'
plotpath = f'{WEB_ROOT}/plots'


pconf[None, None, 'cb_orientation'] = 'vertical'
pconf[None,None,'plotpath'] = plotpath
pconf[None,None,'orocolor'] = None
pconf[None,None,'meridians'] = np.arange(-180,180,60)
pconf[None,None,'parallels'] = np.arange(-60,61,30)

pconfl[None,None,'linewidths'] = [1,]

pconf[None,'Geopotential','cmap'] = cm.KPiRdYl1
pconf[None,'Geopotential (AIFS)','cmap'] = cm.KPiRdYl1
pconf[None,'Geopotential (Google GraphCast)','cmap'] = cm.KPiRdYl1
pconf[None,'Potential vorticity','cmap'] = cm.WYlRd
pconf[None,'Deformation','cmap'] = cm.defabs
pconf[None,'Wind speed','cmap'] = cm.WYlGn
pconf[None,'10m Wind speed','cmap'] = cm.WYlGn

pconf[None,'Temperature','cmap'] = cm.RdYlCyBu2
pconf[None,'2m Temperature','cmap'] = cm.RdYlCyBu2
pconf[None,'Temperature anomaly','cmap'] = cm.RdYlCyBu2
pconf[None,'Potential temperature','cmap'] = cm.RdYlCyBu2
pconf[None,'Equivalent potential temperature','cmap'] = cm.Greys

pconf[None,'Sea-surface temperature','cmap'] = cm.RdYlCyBu2
pconf[None,'Sea-surface temperature anomaly','cmap'] = cm.RdYlCyBu2
pconf[None,'Sea-surface salinity','cmap'] = cm.viridis_r
pconf[None,'Surface current speed','cmap'] = cm.RdYlCyBu2

pconf[None,'Probability of 850 hPa temperatures below the 30-percentile','cmap'] = cm.Blues
pconf[None,'Probability of 850 hPa temperatures above the 70-percentile','cmap'] = cm.Oranges

pconf[None,'Probability of 500 hPa geopotential below the 30-percentile','cmap'] = cm.Greys
pconf[None,'Probability of 500 hPa geopotential above the 70-percentile','cmap'] = cm.Reds

pconf[None,'Specific humidity','cmap'] = cm.WYlBuKPi
pconf[None,'Total column water vapour','cmap'] = cm.WYlBuKPi
pconf[None,'Column integral water vapour transport','cmap'] = cm.WYlBuKPi
pconf[None,'Total precipitation','cmap'] = cm.WBuPi2

pconf[None,'Low cloud cover','cmap'] = cm.KBu
pconf[None,'Mid-level cloud cover','cmap'] = cm.KOr
pconf[None,'High cloud cover','cmap'] = cm.gray

pconf[None,'Cyclone occurrence','cmap'] = cm.Blues
pconf[None,'Jet occurrence within 300 km','cmap'] = cm.Blues
pconf[None,'Anomalous MTA occurrence within 300 km','cmap'] = cm.PiGn2
pconf[None,'Anomalous cyclone occurrence','cmap'] = cm.seismic_r

pconf[None,'Cold-air outbreak index','cmap'] = None # Assumes range 1-15 with extend=both
c1, c2, c3, c4 = cm.Blues, cm.Purples, cm.Reds, cm.Oranges
pconf[None,'Cold-air outbreak index','colors'] = [
        'w', c1(0.2), c1(0.4), c1(0.6),
        c2(0.1), c2(0.3), c2(0.5), c2(0.7),
        c3(0.2), c3(0.4), c3(0.6), c3(0.8),
        c4(0.3), c4(0.5), c4(0.7), c4(0.9),
]

pconf [None,'Geopotential','hook'] = lambda z: z/98.1 # from m/s^2 to gpdm
pconfl[None,'Geopotential','hook'] = lambda z: z/98.1
pconf [None,'Geopotential (AIFS)','hook'] = lambda z: z/98.1 # from m/s^2 to gpdm
pconfl[None,'Geopotential (AIFS)','hook'] = lambda z: z/98.1
pconf [None,'Geopotential (Google GraphCast)','hook'] = lambda z: z/98.1 # from m/s^2 to gpdm
pconfl[None,'Geopotential (Google GraphCast)','hook'] = lambda z: z/98.1
pconf [None,'Potential vorticity','hook'] = lambda pv: np.abs(pv)*1.0e6 # from SI to abs(PVU)
pconfl[None,'Potential vorticity','hook'] = lambda pv: np.abs(pv)*1.0e6
pconf [None,'Temperature','hook'] = lambda t: t - 273.15
pconfl[None,'Temperature','hook'] = lambda t: t - 273.15
pconf [None,'2m Temperature','hook'] = lambda t: t - 273.15
pconfl[None,'2m Temperature','hook'] = lambda t: t - 273.15
pconf [None,'Sea-surface temperature','hook'] = lambda t: t - 273.15
pconfl[None,'Sea-surface temperature','hook'] = lambda t: t - 273.15
pconf [None,'Surface current speed','hook'] = lambda ff: ff*100.0
pconfl[None,'Surface current speed','hook'] = lambda ff: ff*100.0

pconf [None,'Specific humidity','hook'] = lambda q: q*1.0e3
pconfl[None,'Specific humidity','hook'] = lambda q: q*1.0e3

pconf [None,'Sea-level pressure','hook'] = lambda msl: msl/1.0e2
pconfl[None,'Sea-level pressure','hook'] = lambda msl: msl/1.0e2
pconf [None,'Sea-level pressure (AIFS)','hook'] = lambda msl: msl/1.0e2
pconfl[None,'Sea-level pressure (AIFS)','hook'] = lambda msl: msl/1.0e2
pconf [None,'Sea-level pressure (Google GraphCast)','hook'] = lambda msl: msl/1.0e2
pconfl[None,'Sea-level pressure (Google GraphCast)','hook'] = lambda msl: msl/1.0e2
pconf [None,'Change in sea-level pressure since previous forecast','hook'] = lambda msl: msl/1.0e2
pconfl[None,'Change in sea-level pressure since previous forecast','hook'] = lambda msl: msl/1.0e2
pconf [None,'Ensemble ctrl sea level pressure','hook'] = lambda msl: msl/1.0e2
pconfl[None,'Ensemble ctrl sea level pressure','hook'] = lambda msl: msl/1.0e2
pconf [None,'Ensemble mean sea level pressure','hook'] = lambda msl: msl/1.0e2
pconfl[None,'Ensemble mean sea level pressure','hook'] = lambda msl: msl/1.0e2
pconfl[None,'Sea-level pressure','alpha'] = 0.8
pconf [None,'Total precipitation','hook'] = lambda trr: trr + 1.0e-100
pconfl[None,'Total precipitation','hook'] = lambda trr: trr + 1.0e-100

pconfl[None, 'perc', 'scale'] = [0.5, 1.5, 3.5, 15.5, 17.5, 18.5, ]
pconfl[None, 'perc', 'linewidths'] = 1.5

# the end
