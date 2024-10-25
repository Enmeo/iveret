#!/usr/bin/env python
# -*- encoding: utf-8

import copy

import matplotlib as mpl
mpl.use('Agg')

from plotconfig import *
from settings.common2 import *

import dynlib.diag
import dynlib.detect
import dynlib.thermodyn
import dynlib.utils

from current_fc_arome import get_current_fc_arome



q_map = {
    '2m Temperature': 'air_temperature_2m',
    '2m Relative humidity': 'relative_humidity_2m',
    'Cloud base altitude': 'cloud_base_altitude',
    'Temperature': 'air_temperature_pl',
    'Specific humidity': 'specific_humidity_pl',
    'Sea-level pressure': 'air_pressure_at_sea_level',
    '10m Wind barbs': ('x_wind_10m', 'y_wind_10m'),
    '10m Wind gusts': 'wind_speed_of_gust',
    'Wind barbs': ('x_wind_pl', 'y_wind_pl'),
    'Vertical wind': 'upward_air_velocity_pl',
    'Sea-surface temperature': 'SFX_SST',
    'Sea ice concentration': 'SFX_SIC',
}


def get_single(fc_str, plev, q):
    fname = f'{fc_str}/arome.{fc_str}.{plev}.{q}'
    try:
        f, dat, static = metopen(fname, q)
        dat = dat.squeeze()
        if plev in mask:
            dat[mask[plev]] = np.nan
    except:
        dat = None

    return dat


def get(fc_str, level, var):
    plev = level2plev(level)
    if var in q_map:
        q = q_map[var]
    else:
        raise ValueError(f'Unknown variable `{var}`.')
    
    if type(q) == str:
        dat = get_single(fc_str, plev, q)
    else:
        dat = tuple([])
        for q_single in q:
            dat += (get_single(fc_str, plev, q_single), )

    return dat


def get_ff(fc_str, level, var):
    plev = level2plev(level)
    u = get_single(fc_str, plev, 'x_wind_pl')
    v = get_single(fc_str, plev, 'y_wind_pl')

    return np.sqrt(u**2 + v**2)

def get_ff10(fc_str, level, var):
    u10 = get_single(fc_str, 'sfc', 'x_wind_10m')
    v10 = get_single(fc_str, 'sfc', 'y_wind_10m')

    return np.sqrt(u10**2 + v10**2)

def get_cao(fc_str, level, var):
    t = get_single(fc_str, '850', 'air_temperature_pl')
    msl = get_single(fc_str, 'sfc', 'air_pressure_at_sea_level')
    sst = get_single(fc_str, 'sfc', 'SFX_SST')

    CAOi = dynlib.detect.cold_air_outbreak_index(t, msl, sst, sst < 272.16, np.isnan(sst))
    CAOi[np.isnan(CAOi)] = 0.0

    return CAOi

def get_tp(fc_str, level, var):
    tpc = get_single(fc_str, 'sfc', 'precipitation_amount_acc')
    tp = np.zeros(tpc.shape)
    tp[1:,::] = (tpc[1:,::] - tpc[:-1,::])/3.0

    return tp

def get_sthf(fc_str, level, var):
    sshf = get_single(fc_str, 'sfc', 'integral_of_surface_downward_sensible_heat_flux_wrt_time')
    slhf1 = get_single(fc_str, 'sfc', 'integral_of_surface_downward_latent_heat_evaporation_flux_wrt_time')
    slhf2 = get_single(fc_str, 'sfc', 'integral_of_surface_downward_latent_heat_sublimation_flux_wrt_time')
    sthf = sshf + slhf1 + slhf2

    sthff = np.zeros(sthf.shape)
    sthff[1:,::] = (sthf[:-1,::] - sthf[1:,::])/10800.0

    return sthff


get_special = {
    'Wind speed': get_ff,
    '10m Wind speed': get_ff10,
    'Cold-air outbreak index': get_cao,
    'Total precipitation': get_tp,
    'Surface total heat flux': get_sthf,
}


# -----------------------------------------------------------------------------

if __name__ == '__main__':
    # Most recent available data
    forecast = get_current_fc_arome()
    
    # Override
    #forecast = dt(2019,8,27,18)
    plot_only_init = False
    
    print('Plotting the AROME %s forecasts' % forecast.strftime('%Y-%m-%d %H'))
    
    # Domains to be plotted here (i.e. NOT we60)
    domainnames = ['vestland', 'snorway', 'scandes']
    
    plots = [plotter(domainname, domains[domainname], 'no', plotname, plot)
            for domainname in domainnames for plotname, plot in plots['no'][domainname].items()]
    #plots = [plotter(domainname, domains[domainname], 'no', plotname, plot)
    #        for domainname, plots_by_domain in plots['no'].items() for plotname, plot in plots_by_domain.items()
    #        if plotname == 'ff10_gusts']
    
    fc_str = forecast.strftime('%Y%m%dT%HZ')
    conf.datapath.insert(1, '/share/base/metno')
    
    # Load surface pressure to be able to mask areas under ground
    plev, q = 'sfc', 'surface_air_pressure'
    fname = f'{fc_str}/arome.{fc_str}.{plev}.{q}'
    data = {}
    f, data[plev,q], static = metopen(fname, q)
    mask = {}
    for plev, pthres in [('850', 850.0e2), ('925', 925.0e2), ]:
        mask[plev] = data['sfc','surface_air_pressure'].squeeze() < pthres
    
    for plot in plots:
        for plev, q in plot.requires:
            if (plev,q) in data:
                continue

            if q in get_special:
                data[plev,q] = get_special[q](fc_str, plev, q)
            else:
                data[plev,q] = get(fc_str, plev, q)
    
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
            if type(data[q]) == np.ndarray:
                data_inst[q] = data[q][tidx]
            else:
                data_inst[q] = tuple(dat_[tidx] for dat_ in data[q])
        
        for plot in plots:
            plot.plot(data_inst, static, forecast, date)
            plt.close()

    print('Creating page for forecasts from %s.' % forecast.strftime('%d.%m.%Y, %H UTC'))

    fclist = [forecast - td(0.25)*i for i in range(29)]
    leadlist = range(0,67,3)
    leadlist_link = range(0,67,6)
    render_webpage('vestland', 'no', forecast, fclist, leadlist, leadlist_link)
    render_webpage('snorway', 'no', forecast, fclist, leadlist, leadlist_link)
    render_webpage('scandes', 'no', forecast, fclist, leadlist, leadlist_link)

# the end
