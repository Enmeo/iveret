#!/usr/bin/env python
# -*- encoding: utf-8

import numpy as np

from .common import conf, pconf, pconfl, basepath, plotpath, cm, proj


conf.datapath.insert(1, '/share/base/ecmwf')

landmask = np.load(basepath+'/settings/ecmwf_fc_sea_mask.npy')
landmask_hr = np.load(basepath+'/settings/ecmwf_hrfc_sea_mask.npy')

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

pconf [None,'z','hook'] = lambda z: z/98.1
pconfl[None,'z','hook'] = lambda z: z/98.1
pconf [None,'pv','hook'] = lambda pv: pv*1.0e6
pconfl[None,'pv','hook'] = lambda pv: pv*1.0e6
pconf [None,'q','hook'] = lambda q: q*1.0e3
pconfl[None,'q','hook'] = lambda q: q*1.0e3
pconf [None,'defabs','hook'] = lambda defabs: defabs*1.0e5
pconfl[None,'defabs','hook'] = lambda defabs: defabs*1.0e5
pconf [None,'msl','hook'] = lambda msl: msl/1.0e2
pconfl[None,'msl','hook'] = lambda msl: msl/1.0e2
pconf [None,'sst','hook'] = sst_mask_offset
pconfl[None,'sst','hook'] = sst_mask_offset
pconf [None,'siconc','hook'] = mask_land
pconfl[None,'siconc','hook'] = mask_land
pconf [None,'crr','hook'] = lambda crr: crr*1.0e3 + 1.0e-100
pconfl[None,'crr','hook'] = lambda crr: crr*1.0e3 + 1.0e-100
pconf [None,'lsrr','hook'] = lambda lsrr: lsrr*1.0e3 + 1.0e-100
pconfl[None,'lsrr','hook'] = lambda lsrr: lsrr*1.0e3 + 1.0e-100
pconf [None,'trr','hook'] = lambda trr: trr*1.0e3 + 1.0e-100
pconfl[None,'trr','hook'] = lambda trr: trr*1.0e3 + 1.0e-100
pconf [None,'rh2m','hook'] = lambda rh: rh/100.0
pconfl[None,'rh2m','hook'] = lambda rh: rh/100.0

# that's it
