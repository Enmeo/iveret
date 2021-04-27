#!/usr/bin/env python
# -*- encoding: utf-8

import copy

import matplotlib as mpl
mpl.use('Agg')
import matplotlib.dates as mdates

from dynlib.shorthands import np, plt, metopen, dt
from settings.ecmwf import *

import dynlib.utils

from current_fc import *

from topens.PersistentGraph.persistentgraph import *
from topens.PersistentGraph.plots import *


######################################################
# The base of _everything_

# Genering plot
class plotter(object):
    filetype = 'png'
    fcname = 'ec_for_meteograms'
    
    # Which data is required for the plot
    requires = []
    requires_ens = []
    requires_diagnostic = []
    fmt = '%Y%m%d%H'

    figsize = (8.4,3.6)
    
    # Do the art; to be overriden in derived classes
    def plot(self, ctrl, ens, dateinit):
        self.saveas = f'{self.fcname}_{self.plotname}_from_{dateinit.strftime(self.fmt)}_for_{dateinit.strftime(self.fmt)}.{self.filetype}'

        fi = plt.figure(figsize=self.figsize, dpi=96)
        fi.subplotpars.update(left=0.1, right=0.99, top=0.98, bottom=0.1)
        
        data_available = True
        for q in self.requires:
            data_available &= q in ens and q in ctrl

        if not data_available:
            fi.text(0.5, 0.5, 'Error: Data unavailable', horizontalalignment='center', fontsize=24, bbox=dict(facecolor='red', alpha=0.5))
            plt.savefig(plotpath + '/' + self.saveas)
            return True

        else:
            return False

    def plot_finish(self):
        ax = plt.gca()
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=(0)))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
        ax.xaxis.set_minor_locator(mdates.DayLocator())
        plt.savefig(plotpath + '/' + self.saveas)

        return True


######################################################
# Specific plots

# 2m-Temperature
class t2m(plotter):
    requires = ['t2m']
    plotname = 't2m_bgo'

    def plot(self, ctrl, ens, dateinit):
        done = plotter.plot(self, ctrl, ens, dateinit)
        if done:
            return True
        
        T00 = 273.16
        time = ctrl['time']
        for member in range(ens['t2m'].shape[1]):
            plt.plot(time, ens['t2m'][:,member,bgoj,bgoi]-T00, 'C1', alpha=0.4, linewidth=1)

        plt.plot(time, ctrl['t2m'][:,bgoj,bgoi]-T00, 'k', linewidth=2)

        # Mark zero-degree line (if within plot range)
        xlim = plt.xlim()
        ylim = plt.ylim()
        if ylim[0] < 0 and ylim[1] > 0:
            plt.plot(xlim, (0, 0), 'k', linewidth=0.5)

        # This additional line should not affect the plot limits
        plt.xlim(xlim)
        plt.ylim(ylim)

        plt.ylabel('2m temperature [degC]')
            
        return self.plot_finish()


# 2m-Temperature modalities
class t2m_modalities(plotter):
    requires = ['t2m']
    plotname = 't2m_modal_bgo'

    def plot(self, ctrl, ens, dateinit):
        done = plotter.plot(self, ctrl, ens, dateinit)
        if done:
            return True

        T00 = 273.16
        g = PersistentGraph(
                model_type='KMeans',
                time_axis=mdates.date2num(ctrl['time']),
                members=ens['t2m'][:,:,bgoj,bgoi].T-T00,
                score_type='max_inertia',
        )
        g.construct_graph(verbose=False, quiet=True)

        fig, ax = plot_as_graph(g, ax=plt.gca(), show_vertices=True, show_edges=True, show_std=True)


        # Mark zero-degree line (if within plot range)
        xlim = plt.xlim()
        ylim = plt.ylim()
        if ylim[0] < 0 and ylim[1] > 0:
            plt.plot(xlim, (0, 0), 'k', linewidth=0.5)

        # This additional line should not affect the plot limits
        plt.xlim(xlim)
        plt.ylim(ylim)

        plt.ylabel('2m temperature [degC]')
        plt.xlabel('')
            
        return self.plot_finish()


# 2m-Temperature modalities (naive clustering method)
class t2m_modalities_naive(plotter):
    requires = ['t2m']
    plotname = 't2m_modal_naive_bgo'

    def plot(self, ctrl, ens, dateinit):
        done = plotter.plot(self, ctrl, ens, dateinit)
        if done:
            return True

        T00 = 273.16
        g = PersistentGraph(
                model_type='Naive',
                time_axis=mdates.date2num(ctrl['time']),
                members=ens['t2m'][:,:,bgoj,bgoi].T-T00,
                score_type='max_diameter',
        )
        g.construct_graph(verbose=False, quiet=True)

        fig, ax = plot_as_graph(g, ax=plt.gca(), show_vertices=True, show_edges=True, show_std=True)


        # Mark zero-degree line (if within plot range)
        xlim = plt.xlim()
        ylim = plt.ylim()
        if ylim[0] < 0 and ylim[1] > 0:
            plt.plot(xlim, (0, 0), 'k', linewidth=0.5)

        # This additional line should not affect the plot limits
        plt.xlim(xlim)
        plt.ylim(ylim)

        plt.ylabel('2m temperature [degC]')
        plt.xlabel('')
            
        return self.plot_finish()


# Total column water vapour
class tcwv(plotter):
    requires = ['tcwv']
    plotname = 'tcwv_bgo'

    def plot(self, ctrl, ens, dateinit):
        done = plotter.plot(self, ctrl, ens, dateinit)
        if done:
            return True
        
        time = ctrl['time']
        for member in range(ens['tcwv'].shape[1]):
            plt.plot(time, ens['tcwv'][:,member,bgoj,bgoi], 'C0', alpha=0.4, linewidth=1)

        plt.plot(time, ctrl['tcwv'][:,bgoj,bgoi], 'k', linewidth=2)
        plt.ylabel('Total column water vapour [kg/m²]')

        # Have yscale start at zero
        ylim = plt.ylim()
        plt.ylim((0, ylim[1]))
            
        return self.plot_finish()


# Total column water vapour modalities
class tcwv_modalities(plotter):
    requires = ['tcwv']
    plotname = 'tcwv_modal_bgo'

    def plot(self, ctrl, ens, dateinit):
        done = plotter.plot(self, ctrl, ens, dateinit)
        if done:
            return True

        g = PersistentGraph(
                model_type='KMeans',
                time_axis=mdates.date2num(ctrl['time']),
                members=ens['tcwv'][:,:,bgoj,bgoi].T,
                score_type='max_inertia',
                k_max=5,
        )
        g.construct_graph(verbose=False, quiet=True)

        fig, ax = plot_as_graph(g, ax=plt.gca(), show_vertices=True, show_edges=True, show_std=True)

        # Have yscale start at zero
        ylim = plt.ylim()
        plt.ylim((0, ylim[1]))

        plt.ylabel('Total column water vapour [kg/m²]')
        plt.xlabel('')
        
        return self.plot_finish()


# Total column water vapour modalities (naive clustering method)
class tcwv_modalities_naive(plotter):
    requires = ['tcwv']
    plotname = 'tcwv_modal_naive_bgo'

    def plot(self, ctrl, ens, dateinit):
        done = plotter.plot(self, ctrl, ens, dateinit)
        if done:
            return True

        g = PersistentGraph(
                model_type='Naive',
                time_axis=mdates.date2num(ctrl['time']),
                members=ens['tcwv'][:,:,bgoj,bgoi].T,
                score_type='max_diameter',
        )
        g.construct_graph(verbose=False, quiet=True)

        fig, ax = plot_as_graph(g, ax=plt.gca(), show_vertices=True, show_edges=True, show_std=True)

        # Have yscale start at zero
        ylim = plt.ylim()
        plt.ylim((0, ylim[1]))

        plt.ylabel('Total column water vapour [kg/m²]')
        plt.xlabel('')
        
        return self.plot_finish()


# Sea-level pressure
class msl(plotter):
    requires = ['msl']
    plotname = 'msl_bgo'

    def plot(self, ctrl, ens, dateinit):
        done = plotter.plot(self, ctrl, ens, dateinit)
        if done:
            return True
        
        time = ctrl['time']
        for member in range(ens['msl'].shape[1]):
            plt.plot(time, ens['msl'][:,member,bgoj,bgoi]/100.0, 'C4', alpha=0.4, linewidth=1)

        plt.plot(time, ctrl['msl'][:,bgoj,bgoi]/100.0, 'k', linewidth=2)
        plt.ylabel('Sea-level pressure [hPa]')
        
        return self.plot_finish()


# Sea-level pressure modalities
class msl_modalities(plotter):
    requires = ['msl']
    plotname = 'msl_modal_bgo'

    def plot(self, ctrl, ens, dateinit):
        done = plotter.plot(self, ctrl, ens, dateinit)
        if done:
            return True

        g = PersistentGraph(
                model_type='KMeans',
                time_axis=mdates.date2num(ctrl['time']),
                members=ens['msl'][:,:,bgoj,bgoi].T/100.0,
                score_type='max_inertia',
                k_max=5,
        )
        g.construct_graph(verbose=False, quiet=True)

        fig, ax = plot_as_graph(g, ax=plt.gca(), show_vertices=True, show_edges=True, show_std=True)

        plt.ylabel('Sea-level pressure [hPa]')
        plt.xlabel('')
        
        return self.plot_finish()


# Sea-level pressure modalities (naive clustering method)
class msl_modalities_naive(plotter):
    requires = ['msl']
    plotname = 'msl_modal_naive_bgo'

    def plot(self, ctrl, ens, dateinit):
        done = plotter.plot(self, ctrl, ens, dateinit)
        if done:
            return True

        g = PersistentGraph(
                model_type='Naive',
                time_axis=mdates.date2num(ctrl['time']),
                members=ens['msl'][:,:,bgoj,bgoi].T/100.0,
                score_type='max_diameter',
        )
        g.construct_graph(verbose=False, quiet=True)

        fig, ax = plot_as_graph(g, ax=plt.gca(), show_vertices=True, show_edges=True, show_std=True)

        plt.ylabel('Sea-level pressure [hPa]')
        plt.xlabel('')
        
        return self.plot_finish()



# -----------------------------------------------------------------------------

bgoj = 10
bgoi = 10

forecast = get_current_fc()
# Override
#forecast = dt(2021,4,27,0)
fcstr = forecast.strftime(DATEFMT)

print('Plotting the ECMWF %s forecasts' % forecast.strftime('%Y-%m-%d %H'))

# Everything
plots = [
    t2m(), 
    t2m_modalities(), 
    t2m_modalities_naive(), 
    tcwv(),
    tcwv_modalities(),
    tcwv_modalities_naive(),
    msl(),
    msl_modalities(),
    msl_modalities_naive(),
]

files_ctrl = [
    f'{fcstr}/ec.ensctrl.{fcstr}.sfc.meteogram.nc',
]
files_ens = [
    f'{fcstr}/ec.ens.{fcstr}.sfc.meteogram.nc',
]

data_ctrl, data_ens = {}, {}
for file_ in files_ctrl:
    f, grid = metopen(file_)
    
    for q in f.variables:
        data_ctrl[q] = dynlib.utils.scale(f.variables[q])

    data_ctrl['time'] = np.array([dt(t.year, t.month, t.day, t.hour) for t in grid.t_parsed])

for file_ in files_ens:
    f = metopen(file_, no_static=True)
    
    for q in f.variables:
        data_ens[q] = dynlib.utils.scale(f.variables[q])

for plot in plots:
    plot.plot(data_ctrl, data_ens, forecast)
    plt.close()
        

# the end
