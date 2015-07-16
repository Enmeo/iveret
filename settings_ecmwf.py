#!/usr/bin/env python
# -*- encoding: utf-8

from settings_common import conf, cm, proj
import dynlib.context.derived as d

# General settings
# ================

# Naming scheme for ECMWF forecasts
conf.datapath.insert(1, '/Data/gfi/metno/ecmwf')
conf.file_std = '%(time)d/ec.for.%(time)d.%(plev)s.%(q)s'

# Set the default output location (e.g. for plots)
conf.plotpath = '/Data/gfi/metno/visualisation/web/plots'

# Variable definitions
# ====================

u = ('u', 'u', 'U component of wind', 'm s**-1')
v = ('v', 'v', 'V component of wind', 'm s**-1')
w = ('w', 'w', 'Vertical velocity', 'Pa s**-1')

pv = ('pv', 'PV', 'Potential vorticity', 'K m**2 kg**-1 s**-1')

z = ('z', 'Z', 'Geopotential', 'm**2 s**-2')
t = ('t', 'T', 'Temperature', 'K')
pt = ('pt', 'th', 'Potential temperature', 'K')

q = ('q', 'q', 'Specific humidity', 'kg kg**-1')

msl = ('msl', 'msl', 'Mean sea level pressure', 'Pa')
ci = ('ci', 'SIC', 'Sea-ice cover', '(0 - 1)')
sst = ('sst', 'SST', 'Sea surface temperature', 'K')
t2m = ('t2m', 'T2', '2 metre temperature', 'K')
tcwv = ('tcwv', 'tv', 'Total column water vapour', 'kg m**-2')
tcw = ('tcw', 'tw', 'Total column water', 'kg m**-2')
u10 = ('u10', 'u10', '10 metre U wind component', 'm s**-1')
v10 = ('v10', 'v10', '10 metre V wind component', 'm s**-1')

cp = ('cp', 'cprec', 'Convective precipitation', 'm')
lsp = ('lsp', 'lprec', 'Large-scale precipitation', 'm')
tcc = ('tcc', 'tcl', 'Total cloud cover', '(0 - 1)')

# Non-dynlib derived variables
tp = ('tp', 'tprec', 'Total precipitation', 'm')
crr = ('crr', 'crr', 'Convective rain rate', 'm h**-1')
lsrr = ('lsrr', 'lsrr', 'Large-scale rain rate', 'm h**-1')
trr = ('trr', 'trr', 'Total rain rate', 'm h**-1')
ff10 = ('ff10', 'ff10', '10 metre wind speed', 'm s**-1')


# 1. Pressure levels
conf.plevs = ['300', '500', '700', '850', '925']
conf.register_variable([u, v, w, z, t, q], conf.plevs)
conf.register_variable([d.ff, d.defabs, d.defang, d.eqpt], ['850', ])

# 2. Potential temperature levels
conf.ptlevs = ['pt300', 'pt315', 'pt330', 'pt350', ]
conf.register_variable([u, v, pv], conf.ptlevs)

# 3. PV-levels
conf.pvlevs = ['pv2000', ]
conf.register_variable([u, v, pt, d.jetaxis, d.jaoff, d.ff], conf.pvlevs)

# 4. Surface variables
conf.sfclevs = ['sfc', ]
conf.register_variable([msl, ci, sst, t2m, tcwv, tcw, u10, v10, ff10, 
	cp, lsp, tp, crr, lsrr, trr, tcc], conf.sfclevs)



def map_tmp():
	return proj.Basemap(projection='lcc', lat_0=58, lat_ts=58, lon_0=-30, resolution='l', 
			width=10800000, height=7200000)
proj.NAfcmap = map_tmp


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
conf.plotf[None,'crr','hook'] = lambda crr: crr*1.0e3 + 1.0e-100
conf.plot[None,'crr','hook'] = lambda crr: crr*1.0e3 + 1.0e-100
conf.plotf[None,'lsrr','hook'] = lambda lsrr: lsrr*1.0e3 + 1.0e-100
conf.plot[None,'lsrr','hook'] = lambda lsrr: lsrr*1.0e3 + 1.0e-100
conf.plotf[None,'trr','hook'] = lambda trr: trr*1.0e3 + 1.0e-100
conf.plot[None,'trr','hook'] = lambda trr: trr*1.0e3 + 1.0e-100

# that's it
