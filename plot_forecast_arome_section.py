#!/usr/bin/env python
# -*- encoding: utf-8

import copy

import matplotlib as mpl
mpl.use('Agg')
mpl.rcParams.update({'font.size': 16})

from dynlib.shorthands import *
from settings.metno import *

import dynlib.thermodyn

from current_fc_arome import get_current_fc_arome



######################################################
# The base of _everything_

# Genering plot
class plotter(object):
    filetype = 'png'
    sect = 'W-E_60'
    fcsrc = 'no'
    domain = 'we60'
    
    # Add colorbar and legend
    decorations = False

    # Which data is required for the plot
    requires=[]
    requires_diagnostic = []
    fmt = '%Y%m%d%H'

    p_limits = (105000, 8000)
    xticks = np.arange(4,15,2)
    cs_labels = None

    figsize = (9.6,4.8)
    figsize_deco = (10.6667,4.8)
    
    # Do the art; to be overriden in derived classes
    def plot(self, data, static, dateinit, datevalid):

        if self.decorations:
            fi = plt.figure(figsize=self.figsize_deco, dpi=96)
        else:
            fi = plt.figure(figsize=self.figsize, dpi=96)

        fi.subplotpars.update(left=0.07, right=0.99, top=0.99, bottom=0.06)
        
        data_available = True
        for qsect in self.requires:
            data_available &= qsect in data

        if not data_available:
            fi.text(0.5, 0.5, 'Error: Data unavailable', horizontalalignment='center', fontsize=24, bbox=dict(facecolor='red', alpha=0.5))
            return True

        else:
            return False


    def plot_finish(self, dateinit, datevalid):
        if self.decorations:
            cbar = plt.colorbar(self.cs, fraction=0.1, orientation='vertical', shrink=0.8, pad=0.03)
            if type(self.cs_labels) == tuple:
                ticks, labels = self.cs_labels
                cbar.set_ticks(ticks)
                cbar.set_ticklabels(labels)

        ax = plt.gca()

        plt.ylim(self.p_limits)
        plt.yticks(np.arange(10000,100001,10000), np.arange(100,1001,100))
        labels = [f'{tick}°E' for tick in self.xticks]
        labels[0] = '     ' + labels[0]
        labels[-1] = labels[-1] + '       '
        plt.xticks(self.xticks, labels)

        ax.set_facecolor('0.7')

        fname = '%s/%s/%s/%s_for_%s.%s' % (
                self.domain, self.plotname, self.fcsrc, 
                dateinit.strftime(self.fmt), datevalid.strftime(self.fmt), 
                self.filetype
        )

        plt.savefig(f'{plotpath}/{fname}')
        plt.close()



######################################################
# Plot archetypes

# Temperature shading and MSLP contours
class pt(plotter):
    def cal_pt(self, data, static):
        if not (self.sect,'pt') in data:
            data[sect,'pt'] = dynlib.thermodyn.theta_from_temp(data[sect,'air_temperature_ml'], data[sect,'p'])

# Wind speed
class ff(plotter):
    def cal_ff(self, data, static):
        if not (self.sect,'ff') in data:
            data[sect,'ff'] = np.sqrt(data[sect,'x_wind_ml']**2.0 + data[sect,'y_wind_ml']**2.0)

# Wind speed shading, potential temperature contours
class ff_pt(ff, pt):
    requires = [('W-E_60', 'air_temperature_ml'), ('W-E_60', 'x_wind_ml'), ('W-E_60', 'y_wind_ml'), 
            ('W-E_60', 'upward_air_velocity_ml'), ]
    requires_diagnostic = [ff.cal_ff, pt.cal_pt, ]
    plotname = 'ff_pt'

    def plot(self, data, static, dateinit, datevalid):
        done = ff.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        vslc = (slice(3,None,6), slice(5,None,10))
        rho = data[self.sect,'p'][vslc] / (287.058 * data[self.sect,'air_temperature_ml'][vslc])
        
        self.cs = plt.contourf(data[self.sect,'x'], data[self.sect,'p'], data[self.sect,'y_wind_ml'], 
                np.arange(-45,46,5), extend='both', cmap='PRGn_r')
        #plt.quiver(data[self.sect,'x'][vslc], data[self.sect,'p'][vslc], 
        #        data[self.sect,'x_wind_ml'][vslc]/55.5555e3, data[self.sect,'upward_air_velocity_ml'][vslc]*rho*9.81)
        plt.quiver(data[self.sect,'x'][vslc], data[self.sect,'p'][vslc], 
                data[self.sect,'x_wind_ml'][vslc], data[self.sect,'upward_air_velocity_ml'][vslc]*rho*9.81,
                width=0.002)

        #plt.contour(data[self.sect,'x'], data[self.sect,'p'], data[self.sect,'y_wind_ml'], 
        #        [-30, 30, ], colors='tab:green', linewidths=1.5)

        plt.contour(data[self.sect,'x'], data[self.sect,'p'], data[self.sect,'pt'], 
                np.arange(250, 451, 5), colors='0.3', linewidths=0.7)
        plt.contour(data[self.sect,'x'], data[self.sect,'p'], data[self.sect,'pt'], 
                [270, 300, 350], colors='0.2', linewidths=2)

        return True

# Wind speed shading, potential temperature contours
class q_pt(pt):
    requires = [('W-E_60', 'specific_humidity_ml'), ('W-E_60', 'air_temperature_ml'), ]
    requires_diagnostic = [pt.cal_pt, ]
    plotname = 'q_pt'

    def plot(self, data, static, dateinit, datevalid):
        done = ff.plot(self, data, static, dateinit, datevalid)
        if done:
            return True
        
        self.cs = plt.contourf(data[self.sect,'x'], data[self.sect,'p'], data[self.sect,'specific_humidity_ml']*1.0e3, 
                np.arange(1,12.1,0.5), extend='both', cmap=cm.WYlBuKPi)
        self.cs_labels = (np.arange(2,13,2), np.arange(2,13,2))

        plt.contour(data[self.sect,'x'], data[self.sect,'p'], data[self.sect,'air_temperature_ml'], 
                [273.16, ], colors='tab:red', linewidths=2)

        plt.contour(data[self.sect,'x'], data[self.sect,'p'], data[self.sect,'pt'], 
                np.arange(250, 451, 5), colors='0.3', linewidths=0.7)
        plt.contour(data[self.sect,'x'], data[self.sect,'p'], data[self.sect,'pt'], 
                [270, 300, 350], colors='0.2', linewidths=2)

        return True

# Wind speed shading, potential temperature contours
class eturb_pt(pt):
    requires = [('W-E_60', 'turbulent_kinetic_energy_ml'), ('W-E_60', 'air_temperature_ml'), ]
    requires_diagnostic = [pt.cal_pt, ]
    plotname = 'eturb_pt'

    def plot(self, data, static, dateinit, datevalid):
        done = ff.plot(self, data, static, dateinit, datevalid)
        if done:
            return True
        
        self.cs = plt.contourf(data[self.sect,'x'], data[self.sect,'p'], np.log10(data[self.sect,'turbulent_kinetic_energy_ml']+1.0e-100), 
                np.arange(-2,1.01,0.2), extend='both', cmap='afmhot_r')
        self.cs_labels = (np.arange(-2,1.01,0.5), [0.01, 0.03, 0.1, 0.3, 1.0, 3.0, 10.0])

        plt.contour(data[self.sect,'x'], data[self.sect,'p'], data[self.sect,'pt'], 
                np.arange(250, 451, 5), colors='0.3', linewidths=0.7)
        plt.contour(data[self.sect,'x'], data[self.sect,'p'], data[self.sect,'pt'], 
                [270, 300, 350], colors='0.2', linewidths=2)

        return True


# -----------------------------------------------------------------------------

# Most recent available data
forecast = get_current_fc_arome()
# Override 
#forecast = dt(2021,7,5,0)
plot_only_init = False

print('Plotting the AROME %s forecasts' % forecast.strftime('%Y-%m-%d %H'))

plots = [
    ff_pt(), 
    q_pt(), 
    eturb_pt(),
]

fc_str = forecast.strftime('%Y%m%dT%HZ')
data = {}
for plot in plots:
    plot.error = False
    for sect, q in plot.requires:
        if (sect,q) in data:
            continue

        fname = f'{fc_str}/arome.{fc_str}.sect.{sect}.{q}'
        try:
            f, data[sect,q], static = metopen(fname, q)
            data[sect,q] = data[sect,q].squeeze()
        except:
            plot.error = True
    
    if not plot.error:
        if not (sect, 'p') in data:
            ap = f.variables['ap'][:][np.newaxis,:,np.newaxis]
            b = f.variables['b'][:][np.newaxis,:,np.newaxis]
            data[sect,'p'] = ap + b * f.variables['surface_air_pressure'][:,0,:]
        if not (sect, 'x') in data:
            data[sect,'x'] = np.empty(data[sect,'p'].shape)
            data[sect,'x'][:,:,:] = f.variables['longitude'][:,:][np.newaxis,np.newaxis,0,:]

        for fun in plot.requires_diagnostic:
            fun(plot, data, static)

for tidx, date in zip(range(len(static.t)), static.t_parsed):
    # Plot only 3-hourly data to speed up plotting
    if not date.hour % 3 == 0:
        continue

    # Plot only initial time step
    if plot_only_init and not date == forecast:
        continue

    data_inst = {}
    for q in data:
        data_inst[q] = data[q][tidx]
    
    for plot in plots:
        plot.plot(data_inst, static, forecast, date)
        plot.plot_finish(forecast, date)


# the end
