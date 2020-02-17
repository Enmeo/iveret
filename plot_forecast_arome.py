#!/usr/bin/env python
# -*- encoding: utf-8

import copy

import matplotlib as mpl
mpl.use('Agg')

from dynlib.shorthands import *
from settings.metno import *

import dynlib.diag

from current_fc_arome import get_current_fc_arome


######################################################
# The base of _everything_

# Genering plot
class plotter(object):
    filetype = 'png'
    fcname = 'no_for'
    
    # Add colorbar and legend
    decorations = False

    # Which data is required for the plot
    requires=[]
    requires_diagnostic = []
    fmt = '%Y%m%d%H'

    std_plotconf = {
        'm': proj.SNorwaymap,
        'coastcolor': 'k',
        'coastwidth': 0.5,
        'grid_alpha': 0.25,
        'grid_linestyle': '-',
        'grid_latmax': 90,
        'show': False,
        'title': None,
    }
    
    figsize = (6.4,6.4)
    figsize_deco = (7.27273,6.4)
    
    # Do the art; to be overriden in derived classes
    def plot(self, data, static, dateinit, datevalid):
        self.std_plotconf['save'] = '%s_%s_from_%s_for_%s.%s' % (
                self.fcname, self.plotname, 
                dateinit.strftime(self.fmt), datevalid.strftime(self.fmt), 
                self.filetype
        )

        if self.decorations:
            fi = plt.figure(figsize=self.figsize_deco, dpi=96)
            self.std_plotconf['show_legend'] = True
            self.std_plotconf['cb_orientation'] = 'vertical'
            self.std_plotconf['cb_expand_fig_fraction'] = 0.12
            self.std_plotconf['cb_shrink'] = 0.65
            
        else:
            fi = plt.figure(figsize=self.figsize, dpi=96)
            self.std_plotconf['cb_disable'] = True

        fi.subplotpars.update(left=0.001, right=0.999, top=0.999, bottom=0.001)
        
        data_available = True
        for qplev in self.requires:
            data_available &= qplev in data

        if not data_available:
            fi.text(0.5, 0.5, 'Error: Data unavailable', horizontalalignment='center', fontsize=24, bbox=dict(facecolor='red', alpha=0.5))
            plt.savefig(conf.plotpath + '/' + self.std_plotconf['save'])
            return True

        else:
            return False


class Scandes(plotter):
    fcname = plotter.fcname + '_full'

    std_plotconf = copy.copy(plotter.std_plotconf)
    std_plotconf['m'] = proj.Scandimap

    figsize = (5.5,5.9)
    figsize_deco = (6.25,5.9)


######################################################
# Plot archetypes

# Temperature shading and MSLP contours
class t_msl(plotter):
    pass

# Wind speed
class div(plotter):
    def cal_div(self, data, plev, static):
        if not (plev, 'div') in data:
            data[plev,'div'] = dynlib.diag.div(data[plev,'x_wind_pl'], data[plev,'y_wind_pl'], static.dx, static.dy)

# Wind speed
class ff(plotter):
    def cal_ff(self, data, plev, static):
        if not (plev,'ff') in data:
            data[plev,'ff'] = np.sqrt(data[plev,'x_wind_pl']**2.0 + data[plev,'y_wind_pl']**2.0)

# 10m wind speed
class ff10(ff):
    def cal_ff10(self, data, plev, static):
        if not ('sfc','ff_10m') in data:
            data['sfc','ff_10m'] = np.sqrt(data['sfc','x_wind_10m']**2.0 + data['sfc','y_wind_10m']**2.0)

# Total surface fluxes, and surface flux ratios: latent/total, sensible/total
class tshf(plotter):
    def cal_tshf(self, data, plev, static):
        if not ('sfc','tshff') in data:
            total = (data['sfc','integral_of_surface_downward_sensible_heat_flux_wrt_time'] +
                    data['sfc','integral_of_surface_downward_latent_heat_evaporation_flux_wrt_time'] + 
                    data['sfc','integral_of_surface_downward_latent_heat_sublimation_flux_wrt_time'])

            data['sfc','tshff'] = np.zeros(total.shape)
            data['sfc','tshff'][1:,::] = (total[:-1,::] - total[1:,::])/10800.0


# Precipitation
class precip(plotter):
    # Initial precip seems to be a fortran fail value that translates to an all-pink initial plot
    def cal_avg_precip(self, data, plev, static):
        if not ('sfc','precipitation_amount') in data:
            data['sfc','precipitation_amount'] = np.zeros(data['sfc','precipitation_amount_acc'].shape)
            data['sfc','precipitation_amount'][1:,::] = (data['sfc','precipitation_amount_acc'][1:,::] - 
                    data['sfc','precipitation_amount_acc'][0:-1,::])/3.0


######################################################
# Specific plots

# Temperature @ 850 hPa shading, wind barbs, and MSLP contours
class t850_msl(t_msl):
    requires = [('850','air_temperature_pl'), ('850','x_wind_pl'), ('850','y_wind_pl'), ('sfc','air_pressure_at_sea_level')]
    plotname = 't850_msl'

    def plot(self, data, static, dateinit, datevalid):
        done = t_msl.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        overlays = [
            fig.map_overlay_contour(data['sfc','air_pressure_at_sea_level'], static, **conf.plot.merge('sfc', 'msl', 
                contour_labels=True, 
                contour_labels_format='%1.0f',
                linewidths=[1], 
                scale=range(900,1070,2) ) ), 
            fig.map_overlay_contour(data['850','air_temperature_pl'], static, **conf.plot.merge('sfc', 't2m',
                linewidths=[1], 
                linestyles='dashed',
                scale=range(0,2,2) ) ),
            fig.map_overlay_barbs(data['850','x_wind_pl'], data['850','y_wind_pl'], static, **conf.plot.merge('sfc', 'ff10', 
                alpha=0.5,
                linewidths=0.5,
                length=5,
                **self.std_plotconf) ),
        ]
        plotconf = conf.plotf.merge('sfc', 't2m',
                overlays=overlays,
                cmap=cm.t, # Set a colormap
                scale=range(-34,36,2),
                ticks=range(-30,31,10),
                **self.std_plotconf
        )
        fig.map(data['850','air_temperature_pl'], static, **plotconf)

        return True


class t850_msl_Scandes(t850_msl,Scandes):
    requires = [('850','air_temperature_pl'), ('850','x_wind_pl'), ('850','y_wind_pl'), ('sfc','air_pressure_at_sea_level')]
    plotname = 't850_msl'


# Temperature @ 925 hPa shading, wind barbs, and MSLP contours
class t925_msl(t_msl):
    requires = [('925','air_temperature_pl'), ('925','x_wind_pl'), ('925','y_wind_pl'), ('sfc','air_pressure_at_sea_level')]
    plotname = 't925_msl'

    def plot(self, data, static, dateinit, datevalid):
        done = t_msl.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        overlays = [
            fig.map_overlay_contour(data['sfc','air_pressure_at_sea_level'], static, **conf.plot.merge('sfc', 'msl', 
                contour_labels=True, 
                contour_labels_format='%1.0f',
                linewidths=[1], 
                scale=range(900,1070,2) ) ), 
            fig.map_overlay_contour(data['925','air_temperature_pl'], static, **conf.plot.merge('sfc', 't2m',
                linewidths=[1], 
                linestyles='dashed',
                scale=range(0,2,2) ) ),
            fig.map_overlay_barbs(data['925','x_wind_pl'], data['925','y_wind_pl'], static, **conf.plot.merge('sfc', 'ff10', 
                alpha=0.5,
                linewidths=0.5,
                length=5,
                **self.std_plotconf) ),
        ]
        plotconf = conf.plotf.merge('sfc', 't2m',
                overlays=overlays,
                cmap=cm.t, # Set a colormap
                scale=range(-34,36,2),
                ticks=range(-30,31,10),
                **self.std_plotconf
        )
        fig.map(data['925','air_temperature_pl'], static, **plotconf)

        return True


class t925_msl_Scandes(t925_msl,Scandes):
    requires = [('925','air_temperature_pl'), ('925','x_wind_pl'), ('925','y_wind_pl'), ('sfc','air_pressure_at_sea_level')]
    plotname = 't925_msl'


# Specific humidity @ 850 hPa shading, wind barbs, and MSLP contours
class q850_msl(t_msl):
    requires = [('850','specific_humidity_pl'), ('850','air_temperature_pl'), ('850','x_wind_pl'), ('850','y_wind_pl'), ('sfc','air_pressure_at_sea_level')]
    plotname = 'q850_msl'

    def plot(self, data, static, dateinit, datevalid):
        done = t_msl.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        overlays = [
            fig.map_overlay_contour(data['sfc','air_pressure_at_sea_level'], static, **conf.plot.merge('sfc', 'msl', 
                contour_labels=True, 
                contour_labels_format='%1.0f',
                linewidths=[1], 
                scale=range(900,1070,2) ) ), 
            fig.map_overlay_contour(data['850','air_temperature_pl'], static, **conf.plot.merge('sfc', 't2m',
                linewidths=[1], 
                linestyles='solid',
                colors='firebrick',
                scale=range(-5,-3,2) ) ),
            fig.map_overlay_barbs(data['850','x_wind_pl'], data['850','y_wind_pl'], static, **conf.plot.merge('sfc', 'ff10', 
                alpha=0.5,
                linewidths=0.5,
                length=5,
                **self.std_plotconf) ),
        ]
        plotconf = conf.plotf.merge('sfc', 't2m',
                overlays=overlays,
                cmap=cm.q, # Set a colormap
                hook=lambda x: x*1.0e3, # Convert to g/kg
                scale=np.arange(1, 12.1, 0.5),
                ticks=np.arange(2,12.1,2),
                **self.std_plotconf
        )
        fig.map(data['850','specific_humidity_pl'], static, **plotconf)

        return True


class q850_msl_Scandes(q850_msl,Scandes):
    requires = [('850','specific_humidity_pl'), ('850','air_temperature_pl'), ('850','x_wind_pl'), ('850','y_wind_pl'), ('sfc','air_pressure_at_sea_level')]
    plotname = 'q850_msl'


# Temperature @ 925 hPa shading, wind barbs, and MSLP contours
class q925_msl(t_msl):
    requires = [('925','specific_humidity_pl'), ('850','air_temperature_pl'), ('925','x_wind_pl'), ('925','y_wind_pl'), ('sfc','air_pressure_at_sea_level')]
    plotname = 'q925_msl'

    def plot(self, data, static, dateinit, datevalid):
        done = t_msl.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        overlays = [
            fig.map_overlay_contour(data['sfc','air_pressure_at_sea_level'], static, **conf.plot.merge('sfc', 'msl', 
                contour_labels=True, 
                contour_labels_format='%1.0f',
                linewidths=[1], 
                scale=range(900,1070,2) ) ), 
            fig.map_overlay_contour(data['850','air_temperature_pl'], static, **conf.plot.merge('sfc', 't2m',
                linewidths=[1], 
                colors='firebrick',
                linestyles='solid',
                scale=range(-5,-3,2) ) ),
            fig.map_overlay_barbs(data['925','x_wind_pl'], data['925','y_wind_pl'], static, **conf.plot.merge('sfc', 'ff10', 
                alpha=0.5,
                linewidths=0.5,
                length=5,
                **self.std_plotconf) ),
        ]
        plotconf = conf.plotf.merge('sfc', 't2m',
                overlays=overlays,
                cmap=cm.q, # Set a colormap
                hook=lambda x: x*1.0e3, # Convert to g/kg
                scale=np.arange(1, 12.1, 0.5),
                ticks=np.arange(2,12.1,2),
                **self.std_plotconf
        )
        fig.map(data['925','specific_humidity_pl'], static, **plotconf)

        return True


class q925_msl_Scandes(q925_msl,Scandes):
    requires = [('925','specific_humidity_pl'), ('850','air_temperature_pl'), ('925','x_wind_pl'), ('925','y_wind_pl'), ('sfc','air_pressure_at_sea_level')]
    plotname = 'q925_msl'


# Temperature@2m shading and MSLP contours
class t2m_msl(t_msl):
    requires = [('sfc','air_temperature_2m'), ('sfc','air_pressure_at_sea_level')]
    plotname = 't2m_msl'

    def plot(self, data, static, dateinit, datevalid):
        done = t_msl.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        overlays = [
            fig.map_overlay_contour(data['sfc','air_pressure_at_sea_level'], static, **conf.plot.merge('sfc', 'msl', 
                contour_labels=True, 
                contour_labels_format='%1.0f',
                linewidths=[1], 
                scale=range(900,1070,2) ) ), 
            fig.map_overlay_contour(data['sfc','air_temperature_2m'], static, **conf.plot.merge('sfc', 't2m',
                linewidths=[1], 
                linestyles='dashed',
                scale=range(0,2,2) ) ),
        ]
        plotconf = conf.plotf.merge('sfc', 't2m',
                overlays=overlays,
                cmap=cm.t, # Set a colormap
                scale=range(-34,36,2),
                ticks=range(-30,31,10),
                **self.std_plotconf
        )
        fig.map(data['sfc','air_temperature_2m'], static, **plotconf)

        return True


class t2m_msl_Scandes(t2m_msl,Scandes):
    requires = [('sfc','air_temperature_2m'), ('sfc','air_pressure_at_sea_level')]
    plotname = 't2m_msl'


# Surface sensible and latent heat fluxes, near surface wind barbs, dangerous winds.
class shf_wind(tshf, ff10):
    requires = [('sfc','integral_of_surface_downward_latent_heat_evaporation_flux_wrt_time'), 
            ('sfc','integral_of_surface_downward_latent_heat_sublimation_flux_wrt_time'),
            ('sfc','integral_of_surface_downward_sensible_heat_flux_wrt_time'),
            ('sfc','x_wind_10m'), ('sfc','y_wind_10m'), ]
    requires_diagnostic = [('sfc', tshf.cal_tshf), ('sfc', ff10.cal_ff10), ]
    plotname = 'shf_wind'
    
    std_plotconf = ff10.std_plotconf
    std_plotconf['vector_disable_interpolation'] = True
    std_plotconf['vector_space_interval'] = 30

    def plot(self, data, static, dateinit, datevalid):
        done = plotter.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        shf = [-300,-200,-140,-100,-70,-50,-30,-20,-14,-10, 30,50,70,100,140,200,300,500,700,1000,]
        shft = [-10000,]+shf+[10000,]

        overlays = [
            fig.map_overlay_barbs(data['sfc','x_wind_10m'], data['sfc','y_wind_10m'], static, **conf.plot.merge('sfc', 'ff10', 
                linewidths=0.5,
                **self.std_plotconf) ),
            fig.map_overlay_contour(data['sfc','ff_10m'], static, **conf.plot.merge('sfc', 'ff10',
                colors='gold',
                linewidths=[1],
                scale=[17.2, ] ) ),
            fig.map_overlay_contour(data['sfc','ff_10m'], static, **conf.plot.merge('sfc', 'ff10',
                colors='coral',
                linewidths=[1.5],
                scale=[24.5, ] ) ),
            fig.map_overlay_contour(data['sfc','ff_10m'], static, **conf.plot.merge('sfc', 'ff10',
                colors='crimson',
                linewidths=[2],
                scale=[32.7, ] ) ),
        ]

        plotconf = conf.plotf.merge('sfc', 'tshff',
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


class shf_wind_Scandes(shf_wind,Scandes):
    requires = [('sfc','integral_of_surface_downward_latent_heat_evaporation_flux_wrt_time'), 
            ('sfc','integral_of_surface_downward_latent_heat_sublimation_flux_wrt_time'),
            ('sfc','integral_of_surface_downward_sensible_heat_flux_wrt_time'),
            ('sfc','x_wind_10m'), ('sfc','y_wind_10m'), ]
    requires_diagnostic = [('sfc', tshf.cal_tshf), ('sfc', ff10.cal_ff10), ]
    plotname = 'shf_wind' 

    std_plotconf = Scandes.std_plotconf
    std_plotconf['vector_disable_interpolation'] = True
    std_plotconf['vector_space_interval'] = 30
    std_plotconf['cb_shrink'] = 0.65


# Near surface winds.
class ff10_wind(ff10):
    requires = [('sfc','x_wind_10m'), ('sfc','y_wind_10m')]
    requires_diagnostic = [('sfc', ff10.cal_ff10), ]
    plotname = 'ff10_wind' 
    
    std_plotconf = ff10.std_plotconf
    std_plotconf['vector_disable_interpolation'] = True
    std_plotconf['vector_space_interval'] = 10

    def plot(self, data, static, dateinit, datevalid):
        done = plotter.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        overlays = [
            fig.map_overlay_barbs(data['sfc','x_wind_10m'], data['sfc','y_wind_10m'], static, **conf.plot.merge('sfc', 'ff10', 
                linewidths=0.5,
                **self.std_plotconf) ),
        ]
        
        s = np.arange(5.0,32.6,2.5)
        plotconf = conf.plotf.merge('sfc', 'ff10',
                cmap=cm.ff, 
                scale=s,
                extend='both',
                overlays=overlays,
                **self.std_plotconf
        )
        fig.map(data['sfc','ff_10m'], static, **plotconf)

        return True


class ff10_wind_Scandes(ff10_wind,Scandes):
    requires = [('sfc','x_wind_10m'), ('sfc','y_wind_10m')]
    requires_diagnostic = [('sfc', ff10.cal_ff10), ]
    plotname = 'ff10_wind' 

    std_plotconf = Scandes.std_plotconf
    std_plotconf['vector_disable_interpolation'] = True
    std_plotconf['vector_space_interval'] = 30
    std_plotconf['cb_shrink'] = 0.65


# Near-surface relative humidity and total precipitation
class rh2m_tp(precip):
    requires = [('sfc', 'relative_humidity_2m'), ('sfc', 'precipitation_amount_acc')]
    requires_diagnostic = [('sfc', precip.cal_avg_precip), ]
    plotname = 'rh2m_tp'

    def plot(self, data, static, dateinit, datevalid):
        done = precip.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        s=[-1, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.4, 2.0, 3.0, 5.0, 7.0, 10.0] 
        st=[-1, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.4, 2.0, 3.0, 5.0, 7.0, 10.0, 1000.0] 
        overlays = [
            fig.map_overlay_shading(data['sfc','precipitation_amount'], static, **conf.plotf.merge('sfc', 'trr',
                cmap=cm.trr, # Set a colormap
                norm=mpl.colors.BoundaryNorm(st, 256),
                cb_tickspacing='uniform',
                extend='max',
                alpha=0.5,
                scale=s,
                ticks=st,
                **self.std_plotconf ) ), 
        ]

        s=[0.2, 0.4, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.99] 
        st=[-1, 0.2, 0.4, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.99, 10.0] 
        plotconf = conf.plotf.merge('sfc', 'rh2m',
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


class rh2m_tp_Scandes(rh2m_tp,Scandes):
    requires = [('sfc', 'relative_humidity_2m'), ('sfc', 'precipitation_amount_acc')]
    requires_diagnostic = [('sfc', precip.cal_avg_precip), ]
    plotname = 'rh2m_tp'


# Near-surface convergence and 850 hPa vertical wind
class w850_ff(ff):
    requires = [('925', 'x_wind_pl'), ('925', 'y_wind_pl'), ('850', 'upward_air_velocity_pl'), ]
    requires_diagnostic = [('925', ff.cal_ff), ]
    plotname = 'w850_ff'

    def plot(self, data, static, dateinit, datevalid):
        done = precip.plot(self, data, static, dateinit, datevalid)
        if done:
            return True
            
        s=[-10,-3,-1,-0.3,-0.1,0.1,0.3,1.0,3,10.0] 
        st=[-100]+s+[100,]
        w = data['850', 'upward_air_velocity_pl']
        mask = np.logical_and(w > -0.1, w < 0.1)
        w[mask] = np.nan
        overlays = [
            fig.map_overlay_shading(w, static, 
                    **conf.plotf.merge('850','upward_air_velocity_pl',
                cmap='RdGy_r', # Set a colormap
                norm=mpl.colors.BoundaryNorm(st, 256),
                cb_tickspacing='uniform',
                extend='both',
                alpha=0.7,
                scale=s,
                ticks=st,
                **self.std_plotconf) ), 
            fig.map_overlay_contour(data['925', 'ff'], static, **conf.plot.merge('925', 'ff',
                scale=np.arange(5,51,5),
                colors=['tab:blue'],
                linewidths=[0],
                contour_labels=True, 
                contour_labels_format='%1.0f',
                **self.std_plotconf ) ), 
        ]

        plotconf = conf.plotf.merge('925', 'ff',
                scale=np.arange(5,51,5),
                cmap='Blues',
                extend='both',
                overlays=overlays,
                **self.std_plotconf
        )
        plotconf['cb_disable'] = True
        fig.map(data['925','ff'], static, **plotconf)

        return True


class w850_ff_Scandes(w850_ff,Scandes):
    requires = [('925', 'x_wind_pl'), ('925', 'y_wind_pl'), ('850', 'upward_air_velocity_pl'), ]
    requires_diagnostic = [('925', ff.cal_ff), ]
    plotname = 'w850_ff'


# -----------------------------------------------------------------------------

# Most recent available data
forecast = get_current_fc_arome()

# Override 
#forecast = dt(2019,8,27,18)
plot_only_init = False

print('Plotting the AROME %s forecasts' % forecast.strftime('%Y-%m-%d %H'))

plots = [
    t850_msl(),    t850_msl_Scandes(),
    t925_msl(),    t925_msl_Scandes(),
    q850_msl(),    q850_msl_Scandes(),
    q925_msl(),    q925_msl_Scandes(),
    t2m_msl(),     t2m_msl_Scandes(), 
    ff10_wind(),   ff10_wind_Scandes(),
    shf_wind(),    shf_wind_Scandes(),
    rh2m_tp(),     rh2m_tp_Scandes(), 
    w850_ff(),     w850_ff_Scandes(), 
]

fc_str = forecast.strftime('%Y%m%dT%HZ')

# Load surface pressure to be able to mask areas under ground
plev, q = 'sfc', 'surface_air_pressure'
fname = f'{fc_str}/arome.{fc_str}.{plev}.{q}'
data = {}
f, data[plev,q], static = metopen(fname, q)
mask = {}
for plev, pthres in [('850', 850.0e2), ('925', 925.0e2), ]:
    mask[plev] = data['sfc','surface_air_pressure'].squeeze() < pthres

for plot in plots:
    plot.error = False
 
    for plev, q in plot.requires:
        if (plev,q) in data:
            continue

        fname = f'{fc_str}/arome.{fc_str}.{plev}.{q}'
        try:
            f, data[plev,q], static = metopen(fname, q)
            data[plev,q] = data[plev,q].squeeze()
            if plev in mask:
                data[plev,q][mask[plev]] = np.nan
        except:
            plot.error = True
    
    if not plot.error:
        for plev, fun in plot.requires_diagnostic:
            fun(plot, data, plev, static)

# We need to replace the auto-detected x dimension with the alternative lon dimension
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
