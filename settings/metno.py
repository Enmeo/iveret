#!/usr/bin/env python
# -*- encoding: utf-8

from .common import conf, proj, cm


# General settings
# ================

conf.datapath.insert(1, '/home/dfelt/metno/thredds')


# Variable definitions
# ====================

msl = ('msl', 'msl', 'Mean sea level pressure', 'Pa')
t2m = ('t2m', 't2m', '2 metre temperature', 'K')
rh2m = ('rh2m', 'rh2m', '2 metre relative humidity', '(0 - 1)')
sic = ('sic', 'sic', 'Sea ice concentration', '(0 - 1)')
sst = ('sst', 'sst', 'Sea surface temperature', 'K')

sshff = ('sshff', 'sshff', 'Average surface sensibGle heat flux', 'W m**-2')
slhff = ('slhff', 'slhff', 'Average surface latent heat flux', 'W m**-2')
tshff = ('tshff', 'tshff', 'Average total surface heat flux', 'W m**-2')
sshff_frac = ('sshff_frac', 'sshff_frac', 'Fraction of sensible component in average total surface heat flux', 'W m**-2')
slhff_frac = ('slhff_frac', 'slhff_frac', 'Fraction of latent component in average total surface heat flux', 'W m**-2')

# Non-dynlib derived variables
ff10 = ('ff10', 'ff10', '10 metre wind speed', 'm s**-1')
trr = ('trr', 'trr', 'Total rain rate', 'm h**-1')

# 1. Surface variables
conf.sfclevs = ['sfc', ]
conf.register_variable([msl, t2m, rh2m, sic, sst, sshff, slhff, tshff, sshff_frac, slhff_frac, ff10, trr], conf.sfclevs)

##
# Local settings.

conf.plotf[None,'msl','hook'] = lambda msl: msl/1.0e2
conf.plot[None,'msl','hook'] = lambda msl: msl/1.0e2
conf.plotf[None,'t2m','hook'] = lambda t: t - 273.15
conf.plot[None,'t2m','hook'] = lambda t: t - 273.15
conf.plotf[None,'trr','hook'] = lambda trr: trr + 1.0e-100
conf.plot[None,'trr','hook'] = lambda trr: trr + 1.0e-100
conf.plotf[None,'sst','hook'] = lambda sst: sst - 273.15
conf.plot[None,'sst','hook'] = lambda sst: sst - 273.15

# that's it
