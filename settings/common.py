#!/usr/bin/env python
# -*- encoding: utf-8
import matplotlib as mpl

from dynlib.settings import conf, cm, proj
import dynlib.context.plot

import cb

# Set the default output location (e.g. for plots)
#conf.plotpath = '/Data/gfi/metno/visualisation/web/plots'
conf.plotpath = '/data/sci/devel/prj/iveret/web/plots'

cm.z = cb.KPiRdYl1
cm.q = cb.WYlBuKPi
cm.pv = cb.WYlRd
cm.t = cb.RdYlCyBu2
cm.ff = cb.WYlGn
cm.lcc = cb.KBu
cm.mcc = cb.KOr
cm.hcc = cm.gray
cm.trr = cb.WBuPi2
cm.deform = cb.WBuKRd

# the end
