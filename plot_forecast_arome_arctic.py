#!/usr/bin/env python
# -*- encoding: utf-8

import copy

import matplotlib as mpl
mpl.use('Agg')

from dynlib.shorthands import *
from dynlib import utils
from settings.metno import *

import dynlib.detect
import dynlib.thermodyn

from current_fc_arome import get_current_fc_arome
from plot_forecast_arome import plotter, t_msl, ff, ff10, tshf, precip, caos, \
        t850_msl, t925_msl, q850_msl, q925_msl, t2m_msl, ff10_caos, w500_winds, w700_winds, w850_ff


######################################################
# Arctic plot domain

class Arctic(plotter):
    domain = 'barents'

    std_plotconf = copy.copy(plotter.std_plotconf)
    std_plotconf['m'] = proj.Barents_Sea

    figsize = (5.0,6.375)
    figsize_deco = (5.68182,6.375)


######################################################
# Specific plots

# Temperature @ 850 hPa shading, wind barbs, and MSLP contours
class t850_msl_Arctic(t850_msl,Arctic):
    requires = [('850','air_temperature_pl'), ('850','x_wind_pl'), ('850','y_wind_pl'), ('sfc','air_pressure_at_sea_level')]
    plotname = 't850_msl'


# Temperature @ 925 hPa shading, wind barbs, and MSLP contours
class t925_msl_Arctic(t925_msl,Arctic):
    requires = [('925','air_temperature_pl'), ('925','x_wind_pl'), ('925','y_wind_pl'), ('sfc','air_pressure_at_sea_level')]
    plotname = 't925_msl'


# Specific humidity @ 850 hPa shading, wind barbs, and MSLP contours
class q850_msl_Arctic(q850_msl,Arctic):
    requires = [('850','specific_humidity_pl'), ('850','air_temperature_pl'), ('850','x_wind_pl'), ('850','y_wind_pl'), ('sfc','air_pressure_at_sea_level')]
    plotname = 'q850_msl'


# Specific humidity @ 925 hPa shading, wind barbs, and MSLP contours
class q925_msl_Arctic(q925_msl,Arctic):
    requires = [('925','specific_humidity_pl'), ('850','air_temperature_pl'), ('925','x_wind_pl'), ('925','y_wind_pl'), ('sfc','air_pressure_at_sea_level')]
    plotname = 'q925_msl'


# Temperature@2m shading and MSLP contours
class t2m_msl_Arctic(t2m_msl,Arctic):
    requires = [('sfc','air_temperature_2m'), ('sfc','air_pressure_at_sea_level')]
    plotname = 't2m_msl'


# Surface sensible and latent heat fluxes, near surface wind barbs, dangerous winds and MIZ.
# Redefined here, because SST and SIC contours are only added here (not available for std AROME)
class shf_wind_Arctic(tshf, ff10, Arctic):
    requires = [('sfc','integral_of_surface_downward_latent_heat_evaporation_flux_wrt_time'), 
            ('sfc','integral_of_surface_downward_latent_heat_sublimation_flux_wrt_time'),
            ('sfc','integral_of_surface_downward_sensible_heat_flux_wrt_time'),
            ('sfc','x_wind_10m'), ('sfc','y_wind_10m'), 
            ('sfc','SIC'), ('sfc','SST'),]

    requires_diagnostic = [('sfc', tshf.cal_tshf), ('sfc', ff10.cal_ff10), ]
    plotname = 'shf_wind'
    
    std_plotconf = Arctic.std_plotconf
    std_plotconf['vector_disable_interpolation'] = True
    std_plotconf['vector_space_interval'] = 30

    def plot(self, data, static, dateinit, datevalid):
        done = plotter.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        shf = [-300,-200,-140,-100,-70,-50,-30,-20,-14,-10, 30,50,70,100,140,200,300,500,700,1000,]
        shft = [-10000,]+shf+[10000,]

        overlays = [
            fig.map_overlay_barbs(data['sfc','x_wind_10m'], data['sfc','y_wind_10m'], static, **pconfl.merge('sfc', 'ff10', 
                linewidths=0.5,
                **self.std_plotconf) ),
            fig.map_overlay_contour(data['sfc','ff_10m'], static, **pconfl.merge('sfc', 'ff10',
                colors='gold',
                linewidths=[1],
                scale=[17.2, ] ) ),
            fig.map_overlay_contour(data['sfc','ff_10m'], static, **pconfl.merge('sfc', 'ff10',
                colors='coral',
                linewidths=[1.5],
                scale=[24.5, ] ) ),
            fig.map_overlay_contour(data['sfc','ff_10m'], static, **pconfl.merge('sfc', 'ff10',
                colors='crimson',
                linewidths=[2],
                scale=[32.7, ] ) ),
            fig.map_overlay_contour(data['sfc','SIC'], static, **pconfl.merge('sfc', 'sic',
                colors='blueviolet',
                linewidths=[1],
                scale=[0.2, 0.8] ) ),
            fig.map_overlay_contour(data['sfc','SST'], static, **pconfl.merge('sfc', 'sst',
                colors='k',
                alpha=0.5,
                linewidths=[0.7],
                scale=[-1,1,2,3,4,6,7,8,9,11,12,13,14,16,17,18,19] ) ),
            fig.map_overlay_contour(data['sfc','SST'], static, **pconfl.merge('sfc', 'sst',
                colors='k',
                alpha=0.6,
                linewidths=[1],
                scale=np.arange(0,21,5) ) ),
        ]

        plotconf = pconf.merge('sfc', 'tshff',
                cmap=cm.BrBG,
                scale=shf,
                norm=mpl.colors.BoundaryNorm(shft, 256),
                extend='both',
                cb_tickspacing='uniform',
                overlays=overlays,
                **self.std_plotconf
        )
        fig.map(data['sfc','tshff'], static, **plotconf)

        return True


# Near surface winds and 850 hPa frontal volumes
class ff10_caos_Arctic(ff10_caos, Arctic):
    requires = [('sfc','x_wind_10m'), ('sfc','y_wind_10m'), 
            ('sfc', 'air_pressure_at_sea_level'), ('sfc', 'SST'),
			('850','air_temperature_pl'), ]
    requires_diagnostic = [('sfc', ff10.cal_ff10), ('850', caos.cal_cao_index), ]
    plotname = 'ff10_caos'

    std_plotconf = Arctic.std_plotconf
    std_plotconf['vector_disable_interpolation'] = True
    std_plotconf['vector_space_interval'] = 5
    std_plotconf['cb_shrink'] = 0.65


# Near-surface relative humidity, total precipitation and MIZ
# Redefined here, because SIC contours are only added here (not available for std AROME)
class rh2m_tp_Arctic(precip, Arctic):
    requires = [('sfc', 'relative_humidity_2m'), ('sfc', 'precipitation_amount_acc'),
             ('850','air_temperature_pl'), ('sfc', 'SIC'), ]
    requires_diagnostic = [('sfc', precip.cal_avg_precip), ]
    plotname = 'rh2m_tp'

    def plot(self, data, static, dateinit, datevalid):
        done = precip.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        s=[-1, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.4, 2.0, 3.0, 5.0, 7.0, 10.0] 
        st=[-1, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.4, 2.0, 3.0, 5.0, 7.0, 10.0, 1000.0] 
        overlays = [
            fig.map_overlay_shading(data['sfc','precipitation_amount'], static, **pconf.merge('sfc', 'trr',
                norm=mpl.colors.BoundaryNorm(st, 256),
                cb_tickspacing='uniform',
                extend='max',
                alpha=0.5,
                scale=s,
                ticks=st,
                **self.std_plotconf ) ), 
            fig.map_overlay_contour(data['850','air_temperature_pl'], static, **pconfl.merge('sfc', 't',
                linewidths=[1],
                linestyles='solid',
                colors='firebrick',
                scale=range(-5,-3,2) ) ),
            fig.map_overlay_contour(data['sfc','SIC'], static, **pconfl.merge('sfc', 'sic',
                colors='blueviolet',
                linewidths=[1],
                scale=[0.2, 0.8] ) ),
        ]

        s=[0.2, 0.4, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.99] 
        st=[-1, 0.2, 0.4, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.99, 10.0] 
        plotconf = pconf.merge('sfc', 'rh2m',
                cmap=cm.Greys_r, # Set a colormap
                norm=mpl.colors.BoundaryNorm(st, 256),
                #cb_tickspacing='uniform',
                extend='both',
                scale=s,
                ticks=st,
                overlays=overlays,
                **self.std_plotconf
        )
        plotconf['cb_disable'] = True
        fig.map(data['sfc','relative_humidity_2m'], static, **plotconf)

        return True


# Vertical wind @ 500 hPa, 500 hPa wind barbs
class w500_winds_Arctic(w500_winds,Arctic):
    requires = [('500', 'x_wind_pl'), ('500', 'y_wind_pl'), ('500', 'upward_air_velocity_pl'), ]
    plotname = 'w500_winds'

    std_plotconf = Arctic.std_plotconf
    std_plotconf['vector_disable_interpolation'] = True
    std_plotconf['vector_space_interval'] = 5
    std_plotconf['cb_shrink'] = 0.65


# Vertical wind @ 700 hPa, 700 hPa wind barbs
class w700_winds_Arctic(w700_winds,Arctic):
    requires = [('700', 'x_wind_pl'), ('700', 'y_wind_pl'), ('700', 'upward_air_velocity_pl'), ]
    plotname = 'w700_winds'

    std_plotconf = Arctic.std_plotconf
    std_plotconf['vector_disable_interpolation'] = True
    std_plotconf['vector_space_interval'] = 30
    std_plotconf['cb_shrink'] = 0.65


# Near-surface convergence and 850 hPa vertical wind
class w850_ff_Arctic(w850_ff,Arctic):
    requires = [('925', 'x_wind_pl'), ('925', 'y_wind_pl'), ('850', 'upward_air_velocity_pl'), ]
    requires_diagnostic = [('925', ff.cal_ff), ]
    plotname = 'w850_ff'


# -----------------------------------------------------------------------------

if __name__ == '__main__':
    # Most recent available data
    forecast = get_current_fc_arome()
    
    # Override 
    #forecast = dt(2020,7,22,6)
    plot_only_init = False
    
    print('Plotting the AROME Arctic %s forecasts' % forecast.strftime('%Y-%m-%d %H'))
    
    plots = [
        t850_msl_Arctic(),
        t925_msl_Arctic(), 
        q850_msl_Arctic(), 
        q925_msl_Arctic(), 
        ff10_caos_Arctic(),
        t2m_msl_Arctic(), 
        shf_wind_Arctic(), 
        rh2m_tp_Arctic(), 
        w850_ff_Arctic(),
        w500_winds_Arctic(),
        w700_winds_Arctic(),
    ]
    
    fc_str = forecast.strftime('%Y%m%dT%HZ')
    data = {}
    for plot in plots:
        plot.error = False
        for plev, q in plot.requires:
            if (plev,q) in data:
                continue
    
            fname = f'{fc_str}/arome_arctic.{fc_str}.{plev}.{q}'
            try:
                f, data[plev,q], static = metopen(fname, q)
                data[plev,q] = data[plev,q].squeeze()
            except:
                plot.error = True
        
        if not plot.error:
            for plev, fun in plot.requires_diagnostic:
                fun(plot, data, plev, static)
    
    # We need to replace the auto-detected x dimension with the alternative lon dimension and tell dynlib it's a projected grid
    static.x = f.variables['longitude'][::]
    static.y = f.variables['latitude'][::]
    static.gridtype = 'latlon'
    static.prepare_rotation()
    
    
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
            plt.close()


# the end
