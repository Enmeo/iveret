#!/usr/bin/env python
# -*- encoding: utf-8

import copy

import matplotlib as mpl
mpl.use('Agg')

from plotconfig import *
from settings.metno import *

import dynlib.diag
import dynlib.detect
import dynlib.thermodyn
import dynlib.utils

from current_fc_arome import get_current_fc_arome



q_map = {
    '2m Temperature': 'air_temperature_2m',
    'Temperature': 'air_temperature_pl',
    'Specific humidity': 'specific_humidity_pl',
    'Sea-level pressure': 'air_pressure_at_sea_level',
    '10m Wind barbs': ('x_wind_10m', 'y_wind_10m'),
    'Wind barbs': ('x_wind_pl', 'y_wind_pl'),
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

    def cal_tshf(self, data, plev, static):
        if not ('sfc','tshff') in data:
            total = (data['sfc','integral_of_surface_downward_sensible_heat_flux_wrt_time'] +
                    data['sfc','integral_of_surface_downward_latent_heat_evaporation_flux_wrt_time'] + 
                    data['sfc','integral_of_surface_downward_latent_heat_sublimation_flux_wrt_time'])

            data['sfc','tshff'] = np.zeros(total.shape)
            data['sfc','tshff'][1:,::] = (total[:-1,::] - total[1:,::])/10800.0


def cal_avg_precip(self, data, plev, static):
    if not ('sfc','precipitation_amount') in data:
        data['sfc','precipitation_amount'] = np.zeros(data['sfc','precipitation_amount_acc'].shape)
        data['sfc','precipitation_amount'][1:,::] = (data['sfc','precipitation_amount_acc'][1:,::] - 
                data['sfc','precipitation_amount_acc'][0:-1,::])/3.0

def cal_cao_index(self, data, plev, static):
    if not (plev, 'cao_index') in data:
        if ('sfc','SFX_SST') in data:
            plevq_sst = ('sfc','SFX_SST')
        else:
            plevq_sst = ('sfc', 'SST')

        data[plev,'cao_index'] = dynlib.detect.cold_air_outbreak_index(
                data[plev,'air_temperature_pl'].copy(),
                data['sfc','air_pressure_at_sea_level'],
                data[plevq_sst],
                data[plevq_sst] < 272.16,
                np.isnan(data[plevq_sst]),
        )
        data[plev,'cao_index'][np.isnan(data[plev,'cao_index'])] = 0.0



# -----------------------------------------------------------------------------

if __name__ == '__main__':
    # Most recent available data
    forecast = get_current_fc_arome()
    
    # Override 
    #forecast = dt(2019,8,27,18)
    plot_only_init = False
    
    print('Plotting the AROME %s forecasts' % forecast.strftime('%Y-%m-%d %H'))
    
    plots = [plotter(domainname, domains[domainname], 'metno', plotname, plot) 
            for domainname, plots_by_domain in plots['metno'].items() for plotname, plot in plots_by_domain.items()]
    
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
        for plev, q in plot.requires:
            if (plev,q) in data:
                continue

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


# the end
