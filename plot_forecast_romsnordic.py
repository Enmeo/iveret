#!/usr/bin/env python
# -*- encoding: utf-8


import matplotlib as mpl
mpl.use('Agg')

import copy
from mpl_toolkits.basemap import pyproj
from numpy import ma

from dynlib.shorthands import *
from settings.metno import *

from current_fc_kyst import get_current_fc_kyst
from plot_forecast_kyst import rotate_vector_i, plotter, sst_sfccur, sss_sfccur, ff_sfccur


class Scandes(plotter):
    fcname = plotter.fcname + '_full'

    std_plotconf = copy.copy(plotter.std_plotconf)
    std_plotconf['m'] = proj.Scandimap

    figsize = (5.5,6.18)
    figsize_deco = (6.25,6.18)


class BarentsSea(plotter):
    fcname = plotter.fcname + '_barents'

    std_plotconf = copy.copy(plotter.std_plotconf)
    std_plotconf['m'] = proj.BarentsSeamap

    figsize = (5.0,6.375)
    figsize_deco = (5.68182,6.375)


class NAtlantic(plotter):
    fcname = plotter.fcname + '_natlantic'
    
    std_plotconf = copy.copy(plotter.std_plotconf)
    std_plotconf['m'] = proj.NAfcmap

    figsize = (7.2,4.8)
    figsize_deco = (8.18182,4.8)
    


######################################################
# SST and surface currents
class sst_sfccur_Scandes(sst_sfccur,Scandes):
    requires = ['temperature', 'u', 'v']
    plotname = 'sst_sfccur'

    overlay_conf = {'vector_space_interval': 6}


class sst_sfccur_BarentsSea(sst_sfccur,BarentsSea):
    requires = ['temperature', 'u', 'v']
    plotname = 'sst_sfccur'

    overlay_conf = {'vector_space_interval': 5}


class sst_sfccur_NAtlantic(sst_sfccur,NAtlantic):
    requires = ['temperature', 'u', 'v']
    plotname = 'sst_sfccur'

    overlay_conf = {'vector_space_interval': 20}



######################################################
# Surface current speed and direction
class ff_sfccur_Scandes(ff_sfccur,Scandes):
    requires = ['u', 'v']
    plotname = 'ff_sfccur'

    overlay_conf = {'vector_space_interval': 6}


class ff_sfccur_BarentsSea(ff_sfccur,BarentsSea):
    requires = ['u', 'v']
    plotname = 'ff_sfccur'

    overlay_conf = {'vector_space_interval': 5}


class ff_sfccur_NAtlantic(ff_sfccur,NAtlantic):
    requires = ['u', 'v']
    plotname = 'ff_sfccur'

    overlay_conf = {'vector_space_interval': 20}



######################################################
# Surface salinity and currents
class sss_sfccur_Scandes(sss_sfccur,Scandes):
    requires = ['salinity', 'u', 'v']
    plotname = 'sss_sfccur'

    overlay_conf = {'vector_space_interval': 6}


class sss_sfccur_BarentsSea(sss_sfccur,BarentsSea):
    requires = ['salinity', 'u', 'v']
    plotname = 'sss_sfccur'

    overlay_conf = {'vector_space_interval': 5}


class sss_sfccur_NAtlantic(sss_sfccur,NAtlantic):
    requires = ['salinity', 'u', 'v']
    plotname = 'sss_sfccur'

    overlay_conf = {'vector_space_interval': 20}


# -----------------------------------------------------------------------------

if __name__ == '__main__':
    # Most recent available data
    forecast = get_current_fc_kyst()
    plot_only_init = False

    print('Plotting the NorKyst %s forecasts' % forecast.strftime('%Y-%m-%d %H'))

    plots = [
        sst_sfccur_Scandes(), sst_sfccur_BarentsSea(), #sst_sfccur_NAtlantic(),
        ff_sfccur_Scandes(),  ff_sfccur_BarentsSea(),  #ff_sfccur_NAtlantic(), 
        sss_sfccur_Scandes(), sss_sfccur_BarentsSea(), #sss_sfccur_NAtlantic(),
    ]

    fname1 = 'roms_nordic_an_%s.sfc' % forecast.strftime('%Y%m%d%H')
    fname2 = 'roms_nordic_fc_%s.sfc' % forecast.strftime('%Y%m%d%H')
    try:
        #print('Looking for %s' % fname)
        f1, static = metopen(fname1)
        f2, static_ = metopen(fname2)

        # We need to replace the auto-detected x dimension with the alternative lon dimension
        static.x = f1.variables['lon'][::]
        static.y = f1.variables['lat'][::]
        static.gridtype = 'latlon'
        static.t_parsed = np.concatenate((static.t_parsed, static_.t_parsed), axis=0)
        #static.rebuild_grid()
    except ValueError:
        print('Warning: File %s or %s not readable.' % (fname1, fname2))
        class Bunch(dict):
            def __init__(self,**kw):
                dict.__init__(self,kw)
                self.__dict__ = self
        f1 = Bunch(variables=[], close=lambda: None)
        f2 = Bunch(variables=[], close=lambda: None)
        
        t = range(0,67,3)
        static = Bunch(t=t, t_parsed=[forecast + i*td(0,3600) for i in t])

    data = {}
    for plot in plots:
        plot.error = False
        for q in plot.requires:
            if q not in f1.variables or q not in f2.variables:
                print('%s not available!' % q)
                plot.error = True
            elif q not in data:
                data[q] = np.concatenate((
                    utils.scale(f1.variables[q]).squeeze(),
                    utils.scale(f2.variables[q]).squeeze(),
                ), axis=0)
        
        if not plot.error:
            for fun in plot.requires_diagnostic:
                fun(plot, data, static)

    f1.close()
    f2.close()
    
    conf.datapath.insert(1, basepath) # for bathymetry
    f, bathy = metopen('settings/roms_nordic_bathymetry', 'h', no_static=True)
    static.bathymetry = bathy

    for tidx, date in zip(range(len(static.t_parsed)), static.t_parsed):
        # Plot only 3-hourly data to speed up plotting
        if not date.hour % 3 == 0:
            continue

        # Plot only initial time step
        if plot_only_init and not date == forecast:
            continue
        
        print(tidx, date)
        data_inst = {}
        for q in data:
            data_inst[q] = data[q][tidx]
        
        for plot in plots:
            plot.plot(data_inst, static, forecast, date)
            plt.close()


# the end
