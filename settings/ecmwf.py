#!/usr/bin/env python
# -*- encoding: utf-8

import numpy as np

import dynlib.context.ecmwf_fc
import dynlib.context.derived as d

from .common import conf, cm, proj, basepath


# Non-dynlib derived variables
tp = ('tp', 'tprec', 'Total precipitation', 'm')
crr = ('crr', 'crr', 'Convective rain rate', 'm h**-1')
lsrr = ('lsrr', 'lsrr', 'Large-scale rain rate', 'm h**-1')
trr = ('trr', 'trr', 'Total rain rate', 'm h**-1')
ff10 = ('ff10', 'ff10', '10 metre wind speed', 'm s**-1')
rh2m = ('rh2m', 'rh2m', '2 metre relative humidity', '(0 - 1)')
sshff = ('sshff', 'sshff', 'Surface sensible heat flux', 'W m**2')
slhff = ('slhff', 'slhff', 'Surface latent heat flux', 'W m**2')

t_ano = ('t_ano', 't_ano', 'Temperature anomaly', 'K')

perc = ('perc', 'perc', 'Percentiles of given variable', '1')

# Surface variables
conf.sfclevs = ['sfc', ]
conf.register_variable([tp, crr, lsrr, trr, ff10, rh2m, sshff, slhff, perc], conf.sfclevs)

# Derived variables on specific surfaces
conf.register_variable([d.eqpt, d.defabs, t_ano, ], ['850',])
conf.register_variable([d.ff, ], ['pv2000', '700', 'pt300', 'pt315', 'pt330', 'pt350'])

conf.datapath.insert(1, '/share/base/ecmwf')

def map_tmp():
	return proj.Basemap(projection='lcc', lat_0=58, lat_ts=58, lon_0=-30, resolution='l', 
			width=10800000, height=7200000)
proj.NAfcmap = map_tmp


landmask = np.load(basepath+'/settings/ecmwf_fc_sea_mask.npy')
landmask_hr = np.load(basepath+'//settings/ecmwf_hrfc_sea_mask.npy')

def mask_land(data):
	data[landmask] = np.nan
	return data

def sst_mask_offset(sst):
	sst -= 273.15
	sst = mask_land(sst)
	return sst

def mask_land_hr(data):
	data[landmask_hr] = np.nan
	return data

def sst_mask_offset_hr(sst):
	sst -= 273.15
	sst = mask_land_hr(sst)
	return sst

##
# Local settings.

conf.plotf[None,'z','hook'] = lambda z: z/98.1
conf.plot[None,'z','hook'] = lambda z: z/98.1
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
conf.plotf[None,'sst','hook'] = sst_mask_offset
conf.plot[None,'sst','hook'] = sst_mask_offset
conf.plotf[None,'siconc','hook'] = mask_land
conf.plot[None,'siconc','hook'] = mask_land
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
conf.plotf[None, 't_ano', 'cmap'] = cm.t
conf.plotf[None, 'pt', 'cmap'] = cm.t
conf.plotf[None, 'eqpt', 'cmap'] = cm.t
conf.plotf[None, 'q', 'cmap'] = cm.q
conf.plotf[None, 'tcwv', 'cmap'] = cm.q
conf.plotf[None, 'lcc', 'cmap'] = cm.lcc
conf.plotf[None, 'mcc', 'cmap'] = cm.mcc
conf.plotf[None, 'hcc', 'cmap'] = cm.hcc
conf.plotf[None, 'trr', 'cmap'] = cm.trr
conf.plotf[None, 'defabs', 'cmap'] = cm.defabs

conf.plot[None, 'perc', 'scale'] = [0.5, 1.5, 3.5, 15.5, 17.5, 18.5, ]
conf.plot[None, 'perc', 'linewidths'] = 1.5

conf.plotf[None, 'perc', 'cmap'] = cm.t
conf.plotf[None, 'perc', 'scale'] = np.arange(0.5,18.6,1)
conf.plotf[None, 'perc', 'ticks'] = np.arange(0.5,18.6,1)
conf.plotf[None, 'perc', 'ticklabels'] = ['min', '0.1', '0.5', '1', '5', '10', '20', '30', '40', '50', 
		'60', '70', '80', '90', '95', '99', '99.5', '99.9', 'max']

# that's it
