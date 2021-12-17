#!/usr/bin/env python
# -*- encoding: utf-8

import numpy as np

from .common import conf, pconf, pconfl, basepath, plotpath, cm, proj


conf.datapath = ['/share/base/noaa', ]

pconf[None,'z','hook'] = lambda z: z/10.0
pconfl[None,'z','hook'] = lambda z: z/10.0
pconf[None,'pv','hook'] = lambda pv: pv*1.0e6
pconfl[None,'pv','hook'] = lambda pv: pv*1.0e6
pconf[None,'q','hook'] = lambda q: q*1.0e3
pconfl[None,'q','hook'] = lambda q: q*1.0e3
pconf[None,'defabs','hook'] = lambda defabs: defabs*1.0e5
pconfl[None,'defabs','hook'] = lambda defabs: defabs*1.0e5
pconf[None,'msl','hook'] = lambda msl: msl/1.0e2
pconfl[None,'msl','hook'] = lambda msl: msl/1.0e2
pconf[None,'crr','hook'] = lambda crr: crr*1.0e3 + 1.0e-100
pconfl[None,'crr','hook'] = lambda crr: crr*1.0e3 + 1.0e-100
pconf[None,'lsrr','hook'] = lambda lsrr: lsrr*1.0e3 + 1.0e-100
pconfl[None,'lsrr','hook'] = lambda lsrr: lsrr*1.0e3 + 1.0e-100
pconf[None,'trr','hook'] = lambda trr: trr*1.0e3 + 1.0e-100
pconfl[None,'trr','hook'] = lambda trr: trr*1.0e3 + 1.0e-100
pconf[None,'rh2m','hook'] = lambda rh: rh/100.0
pconfl[None,'rh2m','hook'] = lambda rh: rh/100.0




# that's it
