#!/usr/bin/env python
# -*- encoding: utf-8

import numpy as np

import dynlib.context.ecmwf_fc
import dynlib.context.derived as d

from .common import conf, cm, proj


# Non-dynlib derived variables
ci = ('ci', 'ci', 'Sea-ice cover', '(0 - 1)')
tp = ('tp', 'tprec', 'Total precipitation', 'm')
crr = ('crr', 'crr', 'Convective rain rate', 'm h**-1')
lsrr = ('lsrr', 'lsrr', 'Large-scale rain rate', 'm h**-1')
trr = ('trr', 'trr', 'Total rain rate', 'm h**-1')
ff10 = ('ff10', 'ff10', '10 metre wind speed', 'm s**-1')
rh2m = ('rh2m', 'rh2m', '2 metre relative humidity', '(0 - 1)')
sshff = ('sshff', 'sshff', 'Surface sensible heat flux', 'W m**2')
slhff = ('slhff', 'slhff', 'Surface latent heat flux', 'W m**2')

# Surface variables
conf.sfclevs = ['sfc', ]
conf.register_variable([ci, tp, crr, lsrr, trr, ff10, rh2m, sshff, slhff], conf.sfclevs)

# Derived variables on specific surfaces
conf.register_variable([d.eqpt, d.defabs, ], ['850',])
conf.register_variable([d.ff, ], ['pv2000', '700', 'pt300', 'pt315', 'pt330', 'pt350'])

conf.datapath = '/share/base/noaa'

def map_tmp():
	return proj.Basemap(projection='lcc', lat_0=58, lat_ts=58, lon_0=-30, resolution='l', 
			width=10800000, height=7200000)
proj.NAfcmap = map_tmp

##
# Local settings.

conf.plotf[None,'z','hook'] = lambda z: z/10.0
conf.plot[None,'z','hook'] = lambda z: z/10.0
conf.plotf[None,'pv','hook'] = lambda pv: pv*1.0e6
conf.plot[None,'pv','hook'] = lambda pv: pv*1.0e6
conf.plotf[None,'q','hook'] = lambda q: q*1.0e3
conf.plot[None,'q','hook'] = lambda q: q*1.0e3
conf.plotf[None,'defabs','hook'] = lambda defabs: defabs*1.0e5
conf.plot[None,'defabs','hook'] = lambda defabs: defabs*1.0e5
conf.plotf[None,'msl','hook'] = lambda msl: msl/1.0e2
conf.plot[None,'msl','hook'] = lambda msl: msl/1.0e2
conf.plotf[None,'t','hook'] = lambda t: t - 273.15
conf.plot[None,'t','hook'] = lambda t: t - 273.15
conf.plotf[None,'t2m','hook'] = lambda t: t - 273.15
conf.plot[None,'t2m','hook'] = lambda t: t - 273.15
conf.plotf[None,'sst','hook'] = lambda t: t - 273.15
conf.plot[None,'sst','hook'] = lambda t: t - 273.15
conf.plotf[None,'crr','hook'] = lambda crr: crr*1.0e3 + 1.0e-100
conf.plot[None,'crr','hook'] = lambda crr: crr*1.0e3 + 1.0e-100
conf.plotf[None,'lsrr','hook'] = lambda lsrr: lsrr*1.0e3 + 1.0e-100
conf.plot[None,'lsrr','hook'] = lambda lsrr: lsrr*1.0e3 + 1.0e-100
conf.plotf[None,'trr','hook'] = lambda trr: trr*1.0e3 + 1.0e-100
conf.plot[None,'trr','hook'] = lambda trr: trr*1.0e3 + 1.0e-100
conf.plotf[None,'rh2m','hook'] = lambda rh: rh/100.0
conf.plot[None,'rh2m','hook'] = lambda rh: rh/100.0

conf.plot[None, None, 'cb_orientation'] = 'vertical'

conf.plotf[None, 'z', 'cmap'] = cm.z
conf.plotf[None, 'pv', 'cmap'] = cm.pv
conf.plotf[None, 'ff', 'cmap'] = cm.ff
conf.plotf[None, 'ff10', 'cmap'] = cm.ff
conf.plotf[None, 't', 'cmap'] = cm.t
conf.plotf[None, 'pt', 'cmap'] = cm.t
conf.plotf[None, 'eqpt', 'cmap'] = cm.t
conf.plotf[None, 'q', 'cmap'] = cm.q
conf.plotf[None, 'tcwv', 'cmap'] = cm.q
conf.plotf[None, 'lcc', 'cmap'] = cm.lcc
conf.plotf[None, 'mcc', 'cmap'] = cm.mcc
conf.plotf[None, 'hcc', 'cmap'] = cm.hcc
conf.plotf[None, 'trr', 'cmap'] = cm.trr
conf.plotf[None, 'defabs', 'cmap'] = cm.defabs

# that's it
