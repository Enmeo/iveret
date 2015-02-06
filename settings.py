#!/usr/bin/env python
# -*- encoding: utf-8
import matplotlib as mpl

from dynlib_dev.dynpie.settings import conf
import dynlib_dev.dynpie.proj as proj
import dynlib_dev.dynpie.cm as cm


# Adapt the default settings to your needs here, then use 
# >>> from settings import *
# in your personal scripts. 
#
# Examples:
# (1) Add a folder to the datapath which is scanned in metopen. 
#     The first argument is the location within the path, the second place in the example below.
# >>> conf.datapath.insert(1, '/work/csp001/deformation')
# (2) Change the default colormap used in contourf-plots for the quantity 'z'
# >>> conf.contourf.z['cmap'] = plt.cm.RdBu_r
#
# Note that you can always access the default settings by
# >>> from dynlib import default_conf
# >>> default_conf
# >>> print default_conf.datapath
# >>> print default_conf.contourf.Z

# Naming scheme for ECMWF forecasts
conf.file_std = '%(time)d/ec.for.%(time)d.%(plev)s.%(q)s'
#conf.new_variable('tv', 'tcwv')
conf.new_variable('msl','msl')
conf.new_variable('lprec','lsp')
conf.new_variable('cprec','cp')
conf.new_variable('tprec','tp')
conf.new_variable('PV','pv')
conf.new_variable('th','pt')
conf.new_variable('tv','tcwv')
conf.new_variable('tw','tcw')
conf.new_variable('tcl','tcc')
conf.new_variable('u10','u10')
conf.new_variable('v10','v10')

# Add the folder of the forecasts to the PATH, such that reading functions automatically find the data
conf.datapath.insert(1, '/Data/gfi/metno/ecmwf')

cdict = {'red':   ((0.0, 1.0, 1.0), (0.33, 0.30, 0.30),  (0.867, 0.1, 0.1), (1.0, 0.5, 0.5)),
	 'green': ((0.0, 1.0, 1.0), (0.33, 0.65, 0.65),  (0.867, 0.2, 0.2), (1.0, 0.2, 0.2)),
	 'blue':  ((0.0, 1.0, 1.0), (0.33, 0.80, 0.80),  (0.867, 0.6, 0.6), (1.0, 0.8, 0.8))  }
cm.q = mpl.colors.LinearSegmentedColormap('my_defabs',cdict,256)
del cdict

cdict_r = {'red':   ((0.0, 0.1, 0.1), (0.13, 0.1, 0.1),  (0.5, 0.50, 0.50), (0.95, 0.95, 0.95), (1.0, 1.0, 1.0)),
	   'green': ((0.0, 0.1, 0.1), (0.13, 0.2, 0.2),  (0.5, 0.65, 0.65), (0.95, 1.0, 1.0), (1.0, 1.0, 1.0)),
	   'blue':  ((0.0, 0.4, 0.4), (0.13, 0.6, 0.6),  (0.5, 1.00, 1.00), (0.95, 1.0, 1.0), (1.0, 1.0, 1.0))  }
cm.q_r = mpl.colors.LinearSegmentedColormap('my_defabs',cdict_r,256)
del cdict_r

cdict_r = {'red':   ((0.0, 1.0, 1.0), (0.25, 1.0, 1.0),  (0.65, 0.2, 0.2), (1.0, 0.0, 0.0)),
	   'green': ((0.0, 1.0, 1.0), (0.25, 1.0, 1.0),  (0.65, 0.8, 0.8), (1.0, 0.3, 0.3)),
	   'blue':  ((0.0, 1.0, 1.0), (0.25, 0.2, 0.2),  (0.65, 0.2, 0.2), (1.0, 0.0, 0.0))  }
cm.ff = mpl.colors.LinearSegmentedColormap('my_defabs',cdict_r,256)
del cdict_r

cdict_r = {'red':   ((0.0, 1.0, 1.0), (0.25, 1.0, 1.0),  (0.65, 0.2, 0.2), (1.0, 0.3, 0.3)),
	   'green': ((0.0, 1.0, 1.0), (0.25, 1.0, 1.0),  (0.65, 0.8, 0.2), (1.0, 0.0, 0.0)),
	   'blue':  ((0.0, 1.0, 1.0), (0.25, 0.2, 0.2),  (0.65, 0.2, 0.8), (1.0, 0.0, 0.0))  }
cm.ff_beaufort = mpl.colors.LinearSegmentedColormap('my_defabs',cdict_r,256)
del cdict_r

cdict1 = {'red':  ((0.0, 0.0, 0.0),
                   (0.15, 0.1, 0.1),
                   (0.35, 0.1, 0.1),
                   (0.5, 1.0, 1.0),
                   (0.65,1.0, 1.0),
                   (0.85, 0.9, 0.9),
                   (1.0, 0.4, 1.0)),

         'green': ((0.0, 0.0, 0.0),
                   (0.15, 0.2, 0.2),
                   (0.35, 0.8, 0.8),
                   (0.5, 1.0, 1.0),
                   (0.65, 0.8, 0.8),
                   (0.85,0.2, 0.2),
                   (1.0, 0.0, 0.0)),

         'blue':  ((0.0, 0.2, 0.2),
                   (0.15, 0.6, 0.6),
                   (0.35, 0.8, 0.8),
                   (0.5, 1.0, 1.0),
                   (0.65, 0.1, 0.1),
                   (0.85, 0.1, 0.1),
                   (1.0, 0.0, 0.0))
        }

cm.t = mpl.colors.LinearSegmentedColormap('my_defabs',cdict1,256)

del cdict1

cdict2={'red':  ((0.0, 1.0, 1.0),
                   (0.33,1.0, 1.0),
                   (0.66, 1.0, 1.0),
                   #(0.8, 0.3, 0.3),
                   (1.0, 0.4, 0.4)),

         'green': ((0.0, 1.0, 1.0),
                   (0.33, 0.8, 0.8),
                   (0.66, 0.2, 0.2), 
                   #(0.8, 0.0, 0.0),
                   (1.0, 0.0, 0.0)),

         'blue':  ((0.0, 1.0, 1.0),
                   (0.33, 0.1, 0.1),
                   (0.66, 0.1, 0.1), 
                   #(0.8, 0.0, 0.0),
                   (1.0, 0.2, 0.2)),
        }
cm.z = mpl.colors.LinearSegmentedColormap('my_defabs',cdict2,256)

del cdict2

cdict3={'red':    ((0.0, 1.0, 1.0),
                  # (0.1, 0.3, 0.3),
                   (0.3, 0.1, 0.1),
                   (0.5, 0.1, 0.1),
                   (0.6, 0.1, 0.1),
                   (0.8, 0.8, 0.8),
                   (1.0, 0.4, 0.4)),

         'green': ((0.0, 1.0, 1.0), 
                  # (0.1, 0.7, 0.7),
                   (0.3, 0.9, 0.9),
                   (0.5, 0.65,0.65),
                   (0.6, 0.4, 0.4),
                   (0.8, 0.1, 0.1),
                   (1.0, 0.1, 0.1)),

         'blue':  ((0.0, 1.0, 1.0),
                  # (0.1, 0.7, 0.7),
                   (0.3, 0.7, 0.7),
                   (0.5, 0.8, 0.8),
                   (0.6, 1.0, 1.0),
                   (0.8, 0.7, 0.7),
                   (1.0, 0.4, 0.4))
        }
cm.prec = mpl.colors.LinearSegmentedColormap('my_defabs',cdict3,256)

del cdict3

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

cdict4={'red':    ((0.0, 0.9, 0.9),
                   (0.1, 0.4, 0.4),
                   (0.225, 0.1, 0.1),
                   (0.25, 0.1, 0.1),
                   (0.35, 0.1, 0.1),
                   (0.5, 0.9, 0.9),
                   (0.8, 1.0, 1.0),
                   (1.0, 0.5, 0.5)),

         'green': ((0.0, 1.0, 1.0),
                   (0.1, 1.0, 1.0),
                   (0.225, 0.7, 0.7),
                   (0.25, 0.9, 0.9),
                   (0.35, 0.7, 0.7), 
                   (0.5, 0.9, 0.9),
                   (0.8, 0.1, 0.1),
                   (1.0, 0.1, 0.1)),

         'blue':  ((0.0, 1.0, 1.0),
                   (0.1, 1.0, 1.0),
                   (0.225, 0.5, 0.5),
                   (0.25, 0.7, 0.7),
                   (0.35, 0.1, 0.1),
                   (0.5, 0.1, 0.1),
                   (0.8, 0.1, 0.1),
                   (1.0, 0.2, 0.2))
        }
cm.pv = mpl.colors.LinearSegmentedColormap('my_defabs',cdict4,256)

del cdict4

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
cm.pv_new = mpl.colors.LinearSegmentedColormap('my_defabs',cdict7,256)

del cdict7

# Set the default output location (e.g. for plots)
conf.opath = '/Data/gfi/users/csp001/forecasts/web/plots'


def map_tmp():
	return proj.Basemap(projection='lcc', lat_0=58, lat_ts=58, lon_0=-30, resolution='l', 
			width=10800000, height=7200000)
proj.NAfcmap = map_tmp


# that's it
