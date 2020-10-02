#!/usr/bin/env python
# -*- encoding: utf-8

import copy

import matplotlib as mpl
mpl.use('Agg')

from dynlib.shorthands import *
from settings.metno import *

import dynlib.utils

from plot_forecast_arome import plotter, Scandes, get_current_fc_arome


######################################################
# Helper functions

def fill_nan(dat):
    if np.isnan(dat).sum() == 0:
        return dat

    avg = np.nanmean(dat)
    dat -= avg
    dat, __ = dynlib.utils.fill_nan(dat[np.newaxis,:,:])
    dat += avg

    return dat[0,:,:]

# Calculate weights for a 2D-tukey window function of width width
# Zero-weight at boundary, full weight in interior, sin^2-shape in between
def tukey_window(dat, width=120):
    ny, nx = dat.shape[-2:]
    
    taper = np.sin(np.pi/(2*width) * np.arange(width)) ** 2

    wgty = np.ones((ny,))
    wgtx = np.ones((nx,))
    wgty[:width] = taper
    wgty[-width:] = np.minimum(wgty[-width], taper[::-1])
    wgtx[:width] = taper
    wgtx[-width:] = np.minimum(wgtx[-width], taper[::-1])

    wgt = np.ones((ny,nx)) * wgtx[np.newaxis,:]
    wgt[:,width:-width] *= wgty[:,np.newaxis]
    for i in range(width):
        wgt[:,i] = np.minimum(wgt[:,i],wgty)
        wgt[:,-i-1] = np.minimum(wgt[:,i],wgty)

    return wgt

DXY = 2.5e3     # 2.5 km model resolution
def filter_2d(dat, thres=300.0e3):
    datf = np.empty(dat.shape)
    
    wgt = tukey_window(dat, int(thres/DXY))
    ny, nx = dat.shape[-2:]
    kk = np.fft.fftfreq(nx, DXY)  
    ll = np.fft.fftfreq(ny, DXY)
    KK2 = kk[np.newaxis,:]**2 + ll[:,np.newaxis]**2
    freqmask = KK2 <= thres**-2

    for tidx in range(dat.shape[0]):
        dat_ = dat[tidx,:,:]
        mask = np.isnan(dat_)
        dat_ = fill_nan(dat_) * wgt

        dats = np.fft.fft2(dat_)
        datsf = dats * freqmask
        datf[tidx,...] = np.real(np.fft.ifft2(datsf))

        datf[tidx,mask] = np.nan

    return datf

def filter_residual_2d(dat, thres=300.0e3):
    datf = filter_2d(dat, thres)

    return dat - datf


######################################################
# Plot archetypes

# Total surface fluxes, and surface flux ratios: latent/total, sensible/total
class meso_momentum_flux(plotter):
    def cal_meso_momentum_flux(self, data, plev, static):
        if not ('925-700', 'uw_ubal_div') in data:
            #filtr = cal_lanczos2_wgts_2d(N=(60,60))
            
            u925_ubal = filter_residual_2d(data['925', 'x_wind_pl'])
            v925_ubal = filter_residual_2d(data['925', 'y_wind_pl'])
            w925_ubal = filter_residual_2d(data['925', 'upward_air_velocity_pl'])
            u700_ubal = filter_residual_2d(data['700', 'x_wind_pl'])
            v700_ubal = filter_residual_2d(data['700', 'y_wind_pl'])
            w700_ubal = filter_residual_2d(data['700', 'upward_air_velocity_pl'])
            u500_ubal = filter_residual_2d(data['500', 'x_wind_pl'])
            v500_ubal = filter_residual_2d(data['500', 'y_wind_pl'])
            w500_ubal = filter_residual_2d(data['500', 'upward_air_velocity_pl'])

            dz700_925 = (data['700','geopotential_pl'] - data['925','geopotential_pl'])/9.81
            dz500_700 = (data['500','geopotential_pl'] - data['700','geopotential_pl'])/9.81

            data['700-925', 'uw_ubal_div'] = (u700_ubal*w700_ubal - u925_ubal*w925_ubal)/dz700_925
            data['700-925', 'vw_ubal_div'] = (u700_ubal*w700_ubal - u925_ubal*w925_ubal)/dz700_925
            data['500-700', 'uw_ubal_div'] = (u500_ubal*w500_ubal - u700_ubal*w700_ubal)/dz500_700
            data['500-700', 'vw_ubal_div'] = (u500_ubal*w500_ubal - u700_ubal*w700_ubal)/dz500_700

            data['700-925', 'uw_ubal_div_bal'] = filter_2d(data['700-925', 'uw_ubal_div'])
            data['700-925', 'vw_ubal_div_bal'] = filter_2d(data['700-925', 'vw_ubal_div'])
            data['500-700', 'uw_ubal_div_bal'] = filter_2d(data['500-700', 'uw_ubal_div'])
            data['500-700', 'vw_ubal_div_bal'] = filter_2d(data['500-700', 'vw_ubal_div'])



class igw_flxdiv_lvl1(meso_momentum_flux):
    requires = [
        ('925', 'x_wind_pl'), ('925', 'y_wind_pl'), ('925', 'upward_air_velocity_pl'), ('925', 'geopotential_pl'), 
        ('850', 'x_wind_pl'), ('850', 'y_wind_pl'), 
        ('700', 'x_wind_pl'), ('700', 'y_wind_pl'), ('700', 'upward_air_velocity_pl'), ('700', 'geopotential_pl'), 
        ('500', 'x_wind_pl'), ('500', 'y_wind_pl'), ('500', 'upward_air_velocity_pl'), ('500', 'geopotential_pl'), 
    ]
    requires_diagnostic = [(None, meso_momentum_flux.cal_meso_momentum_flux), ]
    plotname = 'igw_flxdiv_lvl1'
    bal = '_bal'
    plev = '850'
    plev_bnds = '700-925'
    
    std_plotconf = plotter.std_plotconf
    std_plotconf['vector_disable_interpolation'] = True
    std_plotconf['vector_space_interval'] = 12

    def plot(self, dat, grid, dateinit, datevalid):
        done = meso_momentum_flux.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        x_acc = dat[self.plev_bnds,f'uw_ubal_div{self.bal}'] * 3600 # From m/s^2 to m/s/h
        y_acc = dat[self.plev_bnds,f'vw_ubal_div{self.bal}'] * 3600 # From m/s^2 to m/s/h
        abs_acc = np.sqrt(x_acc**2 + y_acc**2)
        thres = 0.1
        x_acc[abs_acc < thres] = np.nan
        y_acc[abs_acc < thres] = np.nan
        if not self.bal:
            x_acc *= np.log2(abs_acc)/abs_acc
            y_acc *= np.log2(abs_acc)/abs_acc

        # More dense quivers than standard barbs
        qplotconf = copy.copy(self.std_plotconf)
        qplotconf['vector_space_interval'] //= 2
        overlays = [
            fig.map_overlay_quiver(x_acc, y_acc, grid, plev=self.plev_bnds, q=f'uw_ubal_div{self.bal}',
                #vector_space_interval=4, quiver_length=quiver_length,
                alpha=0.7, zorder=4, hook=None, **qplotconf),
            fig.map_overlay_barbs(dat[self.plev,'x_wind_pl'], dat[self.plev,'y_wind_pl'], grid, plev=self.plev,
                #vector_space_interval=9, vector_disable_interpolation=True, 
                alpha=0.4, zorder=3, barbcolor='C0', flagcolor='C0', linewidths=0.8, **self.std_plotconf),
        ]

        u_acc_scale = np.array([1, 2, 4, 8, 15, 30])/10.0
        plotconf = conf.plotf.merge(self.plev_bnds, f'uw_ubal_div{self.bal}',
                cmap = 'Reds',
                extend = 'both',
                scale = np.log(u_acc_scale),
                ticks = np.log(u_acc_scale),
                ticklabels = list(u_acc_scale),
                hook = lambda x: np.log(x),
                overlays=overlays,
                **self.std_plotconf
        )
        fig.map(abs_acc, grid, plev=self.plev, **plotconf)

        return True


class igw_flxdiv_lvl2(igw_flxdiv_lvl1):
    requires = [
        ('925', 'x_wind_pl'), ('925', 'y_wind_pl'), ('925', 'upward_air_velocity_pl'), ('925', 'geopotential_pl'), 
        ('850', 'x_wind_pl'), ('850', 'y_wind_pl'), 
        ('700', 'x_wind_pl'), ('700', 'y_wind_pl'), ('700', 'upward_air_velocity_pl'), ('700', 'geopotential_pl'), 
        ('500', 'x_wind_pl'), ('500', 'y_wind_pl'), ('500', 'upward_air_velocity_pl'), ('500', 'geopotential_pl'), 
    ]
    requires_diagnostic = [(None, meso_momentum_flux.cal_meso_momentum_flux), ]
    plotname = 'igw_flxdiv_lvl2'
    bal = '_bal'
    plev = '500'
    plev_bnds = '500-700'


class igw_flxdiv_lvl1_Scandes(igw_flxdiv_lvl1,Scandes):
    requires = [
        ('925', 'x_wind_pl'), ('925', 'y_wind_pl'), ('925', 'upward_air_velocity_pl'), ('925', 'geopotential_pl'), 
        ('850', 'x_wind_pl'), ('850', 'y_wind_pl'), 
        ('700', 'x_wind_pl'), ('700', 'y_wind_pl'), ('700', 'upward_air_velocity_pl'), ('700', 'geopotential_pl'), 
        ('500', 'x_wind_pl'), ('500', 'y_wind_pl'), ('500', 'upward_air_velocity_pl'), ('500', 'geopotential_pl'), 
    ]
    requires_diagnostic = [(None, meso_momentum_flux.cal_meso_momentum_flux), ]
    plotname = 'igw_flxdiv_lvl1'

    std_plotconf = Scandes.std_plotconf
    std_plotconf['vector_disable_interpolation'] = True
    std_plotconf['vector_space_interval'] = 36


class igw_flxdiv_lvl2_Scandes(igw_flxdiv_lvl2,Scandes):
    requires = [
        ('925', 'x_wind_pl'), ('925', 'y_wind_pl'), ('925', 'upward_air_velocity_pl'), ('925', 'geopotential_pl'), 
        ('850', 'x_wind_pl'), ('850', 'y_wind_pl'), 
        ('700', 'x_wind_pl'), ('700', 'y_wind_pl'), ('700', 'upward_air_velocity_pl'), ('700', 'geopotential_pl'), 
        ('500', 'x_wind_pl'), ('500', 'y_wind_pl'), ('500', 'upward_air_velocity_pl'), ('500', 'geopotential_pl'), 
    ]
    requires_diagnostic = [(None, meso_momentum_flux.cal_meso_momentum_flux), ]
    plotname = 'igw_flxdiv_lvl2'

    std_plotconf = Scandes.std_plotconf
    std_plotconf['vector_disable_interpolation'] = True
    std_plotconf['vector_space_interval'] = 36



# -----------------------------------------------------------------------------

if __name__ == '__main__':
    # Most recent available data
    forecast = get_current_fc_arome()
    
    # Override 
    #forecast = dt(2020,10,1,6)
    plot_only_init = False
    
    print('Plotting the AROME %s forecasts' % forecast.strftime('%Y-%m-%d %H'))
    
    plots = [
        igw_flxdiv_lvl1(), igw_flxdiv_lvl1_Scandes(),
        igw_flxdiv_lvl2(), igw_flxdiv_lvl2_Scandes(),
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

            if plot_only_init:
                data[plev,q] = data[plev,q][:2,:,:]
        
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
