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

from current_fc import get_current_fc



q_map = {
    '2m Temperature': 't2m',
    'Cloud base altitude': 'clba',
    'Temperature': 't',
    'Specific humidity': 'q',
    'Sea-level pressure': 'msl',
    '10m Wind barbs': ('u10', 'v10'),
    'Wind barbs': ('u', 'v'),
    'Vertical wind': 'w',
}


def get_single(fc_str, plev, q):
    fname = f'{fc_str}/ec.for-hr.{fc_str}.{plev}.{q}'
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


landmask = np.load(VAERKART_ROOT+'/settings/ecmwf_hrfc_sea_mask.npy')
def mask_land(data):
    data[:,landmask] = np.nan

    return data


def get_ff(fc_str, level, var):
    plev = level2plev(level)
    u = get_single(fc_str, plev, 'u')
    v = get_single(fc_str, plev, 'v')

    return np.sqrt(u**2 + v**2)

def get_ff10(fc_str, level, var):
    u10 = get_single(fc_str, 'sfc', 'u10')
    v10 = get_single(fc_str, 'sfc', 'v10')

    return np.sqrt(u10**2 + v10**2)

def get_cao(fc_str, level, var):
    t = get_single(fc_str, '850', 't')
    msl = get_single(fc_str, 'sfc', 'msl')
    sst = get_single(fc_str, 'sfc', 'sst')
    siconc = get_single(fc_str, 'sfc', 'siconc')

    CAOi = dynlib.detect.cold_air_outbreak_index(t, msl, sst, siconc, np.isnan(sst))
    CAOi[np.isnan(CAOi)] = 0.0

    return CAOi

def _normalize_cumulates(cumdat):
    dates = static.t_parsed
    intervals = np.array([(dates[i+1]-dates[i]).total_seconds() for i in range(len(dates)-1)])

    dat = np.zeros(cumdat.shape)
    dat[1:,::] = (cumdat[1:,::] - cumdat[:-1,::])/intervals[:,np.newaxis,np.newaxis]

    return dat

def get_tp(fc_str, level, var):
    lsp = get_single(fc_str, 'sfc', 'lsp')
    cp = get_single(fc_str, 'sfc', 'cp')

    return _normalize_cumulates((lsp+cp)*1000*3600)

def get_sthf(fc_str, level, var):
    sshf = get_single(fc_str, 'sfc', 'sshf')
    slhf = get_single(fc_str, 'sfc', 'slhf')

    return _normalize_cumulates(-sshf-slhf)

def get_siconc(fc_str, level, var):
    siconc = get_single(fc_str, 'sfc', 'siconc')

    return mask_land(siconc)

def get_sst(fc_str, level, var):
    sst = get_single(fc_str, 'sfc', 'sst')

    return mask_land(sst)

def get_rh2m(fc_str, level, var):
    t2m = get_single(fc_str, 'sfc', 't2m')
    d2m = get_single(fc_str, 'sfc', 'd2m')

    e = dynlib.thermodyn.e_sat_liq(d2m)
    rh2m = dynlib.thermodyn.rh_from_e(e, t2m)
    
    return rh2m / 100


get_special = {
    'Wind speed': get_ff,
    '10m Wind speed': get_ff10,
    '2m Relative humidity': get_rh2m,
    'Cold-air outbreak index': get_cao,
    'Total precipitation': get_tp,
    'Surface total heat flux': get_sthf,
    'Sea-surface temperature': get_sst,
    'Sea ice concentration': get_siconc,
}


# -----------------------------------------------------------------------------

if __name__ == '__main__':
    # Most recent available data
    forecast = get_current_fc()
    
    # Override
    #forecast = dt(2019,8,27,18)
    plot_only_init = False
    
    print('Plotting the ECMWF local %s forecasts' % forecast.strftime('%Y-%m-%d %H'))
    
    plots = [plotter(domainname, domains[domainname], 'ec', plotname, plot)
            for domainname, plots_by_domain in plots['ec_local'].items() for plotname, plot in plots_by_domain.items()]
    
    fc_str = forecast.strftime('%Y%m%d%H')
    conf.datapath.insert(1, '/share/base/ecmwf')
    
    # Load surface pressure to be able to mask areas under ground
    plev, q = 'sfc', 'msl'
    fname = f'{fc_str}/ec.for-hr.{fc_str}.{plev}.{q}'
    data = {}
    f, data[plev,q], static = metopen(fname, q)
    mask = {}
    for plev, pthres in [('850', 850.0e2), ('925', 925.0e2), ]:
        mask[plev] = data['sfc','msl'].squeeze() < pthres
    
    for plot in plots:
        for plev, q in plot.requires:
            if (plev,q) in data:
                continue

            if q in get_special:
                data[plev,q] = get_special[q](fc_str, plev, q)
            else:
                data[plev,q] = get(fc_str, plev, q)
    
    for tidx, date in zip(range(len(static.t)), static.t_parsed):
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

    fclist = [forecast - td(0.5)*i for i in range(15)]
    leadlist = range(0,73,3)
    leadlist_link = range(0,73,6)
    render_webpage('scandes', 'ec', forecast, fclist, leadlist, leadlist_link)
    render_webpage('barents', 'ec', forecast, fclist, leadlist, leadlist_link)

# the end
