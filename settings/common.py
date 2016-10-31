#!/usr/bin/env python
# -*- encoding: utf-8

from __future__ import print_function, absolute_import, division, unicode_literals

import matplotlib as mpl

from dynlib.settings import conf, cm, proj
import dynlib.context.plot

from . import cb

# Set the default output location (e.g. for plots)
#conf.plotpath = '/Data/gfi/metno/visualisation/web/plots'
conf.plotpath = '/data/sci/devel/prj/iveret/web/plots'
conf.datapath.insert(1, '/data/sci/data/erai_fc_testdata')

cm.z = cb.KPiRdYl1
cm.q = cb.WYlBuKPi
cm.pv = cb.WYlRd
cm.t = cb.RdYlCyBu2
cm.ff = cb.WYlGn
cm.lcc = cb.KBu
cm.mcc = cb.KOr
cm.hcc = cm.gray
cm.trr = cb.WBuPi2

# the end
