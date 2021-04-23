#!/usr/bin/env python
# -*- encoding: utf-8

from .common import conf, pconf, pconfl, basepath, plotpath, cm, proj


# General settings
# ================

conf.datapath.insert(1, '/share/base/metno_kyst')
conf.datapath.insert(1, '/share/base/metno')


##
# Local settings.

pconf [None,'msl','hook'] = lambda msl: msl/1.0e2
pconfl[None,'msl','hook'] = lambda msl: msl/1.0e2
pconf [None,'trr','hook'] = lambda trr: trr + 1.0e-100
pconfl[None,'trr','hook'] = lambda trr: trr + 1.0e-100

# that's it
