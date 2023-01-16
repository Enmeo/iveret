#!/usr/bin/env python
# -*- encoding: utf-8

import copy

import matplotlib as mpl
mpl.use('Agg')
import scipy.interpolate as interp

from plotconfig import *
from settings.common2 import *

import dynlib.diag
import dynlib.detect
import dynlib.thermodyn
import dynlib.sphere
import dynlib.utils

from current_ext_fc import get_current_fc



q_map = {
}

qf = {
    'viewvt': 'viwve',
    'vinwvt': 'viwvn',
}


# Save expensive intermediate steps to avoid recalculation
CACHE = {}


def get_single(fc_str, fc_str_prev, plev, q):
    fname = f'{fc_str}/ec.ens.{fc_str}.{plev}.{q}'
    try:
        f, dat, static = metopen(fname, qf.get(q, q))
        dat = dat.squeeze()
    except Exception as e:
        print(type(e), e)
        dat = None

    return dat


def get(fc_str, fc_str_prev, level, var):
    plev = level2plev(level)
    if var in q_map:
        q = q_map[var]
    else:
        raise ValueError(f'Unknown variable `{var}`.')
    
    if type(q) == str:
        dat = get_single(fc_str, fc_str_prev, plev, q)
    else:
        dat = tuple([])
        for q_single in q:
            dat += (get_single(fc_str, fc_str_prev, plev, q_single), )

    return dat


def get_mtafreq(fc_str, fc_str_prev, level, var):
    plev = level2plev(level)
    uens = get_single(fc_str, fc_str_prev, plev, 'viewvt')
    vens = get_single(fc_str, fc_str_prev, plev, 'vinwvt')

    f, static = metopen(f'{fc_str}/ec.ens.{fc_str}.sfc.viewvt')
    f.close()

    dynfor.config.nsmooth = 0
    dynfor.config.minlen = 2.0e6
    dynfor.config.jetint_thres = 5.0e-7
    dynfor.config.searchrad = 1.5
    dynfor.config.grid_cyclic_ew = True
    
    # Precalculate distances between points on a lat/lon grid
    green = dynlib.utils.dist_green_latlon(static.x[0,:], static.y[:,0])

    mtafreq = np.empty(uens.shape[0:1] + static.x.shape)
    for tidx in range(uens.shape[0]):
        # MTA detections
        lines, loff = dynlib.detect.jetaxis(10000, 2000, uens[tidx,:,:,:], vens[tidx,:,:,:], static.dx, static.dy)
        koff = loff.astype('i4')
        mask = dynlib.utils.mask_lines(static.x.shape[1], static.x.shape[0], lines, loff)
        
        # Find everything within 300 km of a MTA and save
        mindists = dynlib.utils.dist_from_mask_latlon(mask, green, static.x.shape[1]//2)
        mtafreq[tidx,:,:] = (mindists < 300.0e3).mean(axis=0)
    
    # Take the final 25 days as basic state 
    # TODO: Determine better basic state from ERA5
    mtafreq -= mtafreq[20:,:,:].mean(axis=0)

    # 5-day lowpass filter with reflection boundary conditions
    filtr = dynlib.utils.lanczos_weights_lowpass(10, size=2)
    mtafreq = np.concatenate((mtafreq[:10][::-1], mtafreq, mtafreq[-10:][::-1]), axis=0)
    mtafreq = dynlib.utils.filter_t(mtafreq, filtr)[10:-10,:,:]
    
    return mtafreq


get_special = {
    'Anomalous MTA occurrence within 300 km': get_mtafreq,
}


# -----------------------------------------------------------------------------

if __name__ == '__main__':
    import sys

    # Most recent available data
    forecast = get_current_fc()
    
    # Override
    #forecast = dt(2019,8,27,18)
    plot_only_init = False
    
    print('Plotting the ECMWF local %s forecasts' % forecast.strftime('%Y-%m-%d %H'))

    PLOT_SETS = {
        'test': [],
        'sfc': ['mtafreqa', ],
    }
    
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg in PLOT_SETS:
                plots = [plotter(domainname, domains[domainname], 'ec_ext', plotname, plot)
                    for domainname, plots_by_domain in plots['ec_ext'].items() for plotname, plot in plots_by_domain.items()
                    if plotname in PLOT_SETS[arg]
                ]
                print('Plotting plot set "%s".' % arg)
            else:
                raise ValueError('Unknown plot set "%s".' % arg)
    else:
        plots = [plotter(domainname, domains[domainname], 'ec_ext', plotname, plot)
            for domainname, plots_by_domain in plots['ec_ext'].items() for plotname, plot in plots_by_domain.items()]

        print('No plot set specified, plotting all plot sets.')

    print(len(plots))
    
    fc_str = forecast.strftime('%Y%m%d%H')
    fc_str_prev = '-no-prev-fc-'
    conf.datapath.insert(1, '/share/base/ecmwf_ext')
    
    # Load static information
    plev, q = 'sfc', 'viewvt'
    fname = f'{fc_str}/ec.ens.{fc_str}.{plev}.{q}'
    f, static = metopen(fname)
    
    data = {}
    for plot in plots:
        for plev, q in plot.requires:
            if (plev,q) in data:
                continue

            if q in get_special:
                data[plev,q] = get_special[q](fc_str, fc_str_prev, plev, q)
            else:
                data[plev,q] = get(fc_str, fc_str_prev, plev, q)
    
    for tidx, date in zip(range(len(static.t)), static.t_parsed):
        # Plot only initial time step
        if plot_only_init and not date == forecast:
            continue
    
        data_inst = {}
        for q in data:
            if type(data[q]) == np.ndarray:
                data_inst[q] = data[q][tidx]
            elif type(data[q]) == type(None):
                data_inst[q] = np.empty(data['sfc','viewvt'].shape[1:]) * np.nan
            else:
                data_inst[q] = tuple(dat_[tidx] for dat_ in data[q])
        
        for plot in plots:
            plot.plot(data_inst, static, forecast, date)
            plt.close()

    print('Creating page for forecasts from %s.' % forecast.strftime('%d.%m.%Y, %H UTC'))
    
    if forecast.weekday() == 0:
        fcdays = [0, 4]
    else:
        fcdays = [0, 3]

    fclist = [forecast - td(day + 7*week) for week in range(5) for day in fcdays]
    leadlist = list(range(0,841,12))
    leadlist_link = [24*(week*7 + day) for week in range(5) for day in [0,2,4]] + [840,]

    render_webpage('npolar', 'ec_ext', forecast, fclist, leadlist, leadlist_link)
    render_webpage('spolar', 'ec_ext', forecast, fclist, leadlist, leadlist_link)

# the end
