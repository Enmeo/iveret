#!/usr/bin/env python
# -*- encoding: utf-8
import matplotlib as mpl

from dynlib.settings import conf, cm, proj
import dynlib.context.plot

from cb.clemens_Z_new import test_cm as z_new
from cb.q_high_homogeneous import test_cm as q_new
from cb.pv_jump_homogeneous import test_cm as pv_new
from cb.RdYlCyBu_homogeneous import test_cm as t_new


# Set the default output location (e.g. for plots)
conf.plotpath = './web/plots'


cdict5={'red':    ((0.0, 1.0, 1.0),
                  # (0.1, 0.3, 0.3),
                   (0.4, 0.3, 0.3),
                 #  (0.5, 0.1, 0.1),
                   (0.9, 0.1, 0.1),
                  # (0.9, 0.8, 0.8),
                   (1.0, 0.8, 0.8)),

         'green': ((0.0, 1.0, 1.0), 
                  # (0.1, 0.7, 0.7),
                   (0.4, 0.65, 0.65),
                  # (0.5, 0.4,0.4),
                   (0.9, 0.2, 0.2),
                   #(0.9, 0.1, 0.1),
                   (1.0, 0.1, 0.1)),

         'blue':  ((0.0, 1.0, 1.0),
                  # (0.1, 0.7, 0.7),
                   (0.4, 0.8, 0.8),
                  # (0.5, 0.8, 0.8),
                   (0.9, 0.4, 0.4),
                   #(0.9, 0.7, 0.7),
                   (1.0, 0.7, 0.7))
        }
cm.prec_bl = mpl.colors.LinearSegmentedColormap('my_defabs',cdict5,256)

del cdict5

cdict6 = {'red':  ((0.0, 0.0, 0.0),
                   (0.15, 0.1, 0.1),
                   (0.35, 0.1, 0.1),
                   (0.475, 0.4, 0.4),
                   (0.5, 1.0, 1.0),
                   (0.65,1.0, 1.0),
                   (0.85, 0.9, 0.9),
                   (1.0, 0.4, 1.0)),

         'green': ((0.0, 0.0, 0.0),
                   (0.15, 0.2, 0.2),
                   (0.35, 0.8, 0.8),
                   (0.475, 1.0, 1.0),
                   (0.5, 1.0, 1.0),
                   (0.65, 0.8, 0.8),
                   (0.85,0.2, 0.2),
                   (1.0, 0.0, 0.0)),

         'blue':  ((0.0, 0.2, 0.2),
                   (0.15, 0.6, 0.6),
                   (0.35, 0.8, 0.8),
                   (0.475, 1.0, 1.0),
                   (0.5, 0.6, 0.6),
                   (0.65, 0.1, 0.1),
                   (0.85, 0.1, 0.1),
                   (1.0, 0.0, 0.0))
        }

cm.pt = mpl.colors.LinearSegmentedColormap('my_defabs',cdict6,256)

del cdict6

cdict7={'red':    ((0.0, 1.0, 1.0),
                   (0.125, 0.4, 0.4),
                  # (0.25, 0.1, 0.1),
                   #(0.25, 0.1, 0.1),
                   (0.25, 0.1, 0.1),
                   (0.4, 0.9, 0.9),
                   (0.8, 1.0, 1.0),
                   (1.0, 0.5, 0.5)),

         'green': ((0.0, 1.0, 1.0),
                   (0.1, 1.0, 1.0),
                  # (0.25, 0.7, 0.7),
                   #(0.25, 0.9, 0.9),
                   (0.25, 0.7, 0.7), 
                   (0.4, 0.9, 0.9),
                   (0.8, 0.1, 0.1),
                   (1.0, 0.1, 0.1)),

         'blue':  ((0.0, 1.0, 1.0),
                   (0.1, 1.0, 1.0),
                   #(0.25, 0.5, 0.5),
                   #(0.25, 0.7, 0.7),
                   (0.25, 0.1, 0.1),
                   (0.4, 0.1, 0.1),
                   (0.8, 0.1, 0.1),
                   (1.0, 0.2, 0.2))
        }
cm.pv = mpl.colors.LinearSegmentedColormap('my_defabs',cdict7,256)

del cdict7

cm.z_new = z_new
cm.q_new = q_new
cm.pv_new = pv_new
cm.t_new = t_new


