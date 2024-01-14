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
    'viewvt': 'unknown',
    'vinwvt': 'unknown',
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


# 5-day lowpass filter with reflection boundary conditions
def _filter_l5d(dat):
    filtr = dynlib.utils.lanczos_weights_lowpass(10, size=2)
    dat = np.concatenate((dat[:10][::-1], dat, dat[-10:][::-1]), axis=0)
    dat = dynlib.utils.filter_t(dat, filtr)[10:-10,:,:]

    return dat

# Medio days of each month (for a non-leap year), start counting days at zero
_monthly_medios = [dt(2010,1,15), dt(2010,2,14), dt(2010,3,15), dt(2010,4,15), dt(2010,5,15), dt(2010,6,15), 
                   dt(2010,7,15), dt(2010,8,15), dt(2010,9,15), dt(2010,10,15), dt(2010,11,15), dt(2010,12,15),]
_monthly_doys = np.array([date.timetuple().tm_yday-1 for date in _monthly_medios], dtype='i4')
_monthly_lens = np.concatenate((_monthly_doys[1:] - _monthly_doys[:-1], np.array([31,])), axis=0)
def _interpolate_to_valid_time(percs, dates):
    # Disregard leap days if present (in this case, 30 and 31 December are treated identical)
    doys = np.array([min(364,date.timetuple().tm_yday-1) for date in dates], dtype='i4')

    # Might be all zeros or all ones -> in both cases we need to interpolate between mid Dec and mid Jan
    # Thus firstidx = -1, nextidx = 0
    firstidx = (doys[:,np.newaxis] >= _monthly_doys[np.newaxis,:]).sum(axis=1) % 12 - 1
    nextidx = firstidx + 1
    
    # Difference is negeative for 1 Jan through 14 Jan -> modulo to take into account periodicity
    frac = ((doys - _monthly_doys[firstidx]) % 365 )/_monthly_lens[firstidx]
    
    # Linear interpolation in monthly time segments
    ipercs = percs[firstidx,:,:] * (1-frac[:,np.newaxis,np.newaxis]) + percs[nextidx,:,:] * frac[:,np.newaxis,np.newaxis]
    
    return ipercs


PERC_PATH = '/home/ubuntu/data'
PERC_PERIOD = '1979-2020'
conf.datapath.insert(1, PERC_PATH)
def get_mtafreq(fc_str, fc_str_prev, level, var, static):
    plev = level2plev(level)
    uens = get_single(fc_str, fc_str_prev, plev, 'viewvt')
    vens = get_single(fc_str, fc_str_prev, plev, 'vinwvt')

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

    return _filter_l5d(mtafreq)


def get_cycfreq(fc_str, fc_str_prev, level, var, static):
    mslens = get_single(fc_str, fc_str_prev, 'sfc', 'msl')

    dynfor.config.cyc_minsize = 0.5e6       # in km^2
    dynfor.config.cyc_maxsize = 4.5e6       # in km^2
    dynfor.config.cyc_maxoro = 1500         # in m
    dynfor.config.cyc_mindist = 750         # in km
    dynfor.config.cyc_minprominence = 200   # in Pa
    
    s = mslens.shape
    cycfreq = np.empty(s[0:1]+s[2:])
    for tidx in range(s[0]):
        print(f'{tidx}/{s[0]}')
        cycmask, meta = dynlib.detect.cyclone_by_contour(mslens[tidx,:,:,:], static)
        cycmask[cycmask > 0.5] = 1
        cycfreq[tidx,:,:] = cycmask.mean(axis=0)
    
    # Take the final 25 days as basic state 
    # TODO: Determine better basic state from ERA5
    cycfreq -= cycfreq[20:,:,:].mean(axis=0)

    return _filter_l5d(cycfreq)


def get_prob_cold(fc_str, fc_str_prev, level, var, static):
    mon = int(fc_str[4:6]) - 1
    plev = level2plev(level)
    f, t_percs, fgrid = metopen(f'ea.ans.{PERC_PERIOD}.{plev}.t_percs', 't')
    
    # TODO: interpolate to coarser grid 
    # Percentile index 7 -> 30-percentile
    t_percs = _interpolate_to_valid_time(t_percs[:,7,::3,::3], static.t_parsed)
    
    t = get_single(fc_str, fc_str_prev, plev, 't')
    s = t.shape
    t = _filter_l5d(t.reshape(s[:2] + (np.prod(s[2:]), )) )
    t = t.reshape(s)
    prob = (t <= t_percs[:,np.newaxis,:,:]).mean(axis=1)
    #prob[prob < 0.39] = np.nan

    return prob

def get_prob_warm(fc_str, fc_str_prev, level, var, static):
    mon = int(fc_str[4:6]) - 1
    plev = level2plev(level)
    f, t_percs, fgrid = metopen(f'ea.ans.{PERC_PERIOD}.{plev}.t_percs', 't')
    
    # TODO: interpolate to coarser grid 
    # Percentile index 11 -> 70-percentile
    t_percs = _interpolate_to_valid_time(t_percs[:,11,::3,::3], static.t_parsed)
    
    t = get_single(fc_str, fc_str_prev, plev, 't')
    s = t.shape
    t = _filter_l5d(t.reshape(s[:2] + (np.prod(s[2:]), )) )
    t = t.reshape(s)
    prob = (t >= t_percs[:,np.newaxis,:,:]).mean(axis=1)
    #prob[prob < 0.39] = np.nan

    return prob


get_special = {
    'Anomalous MTA occurrence within 300 km': get_mtafreq,
    'Anomalous cyclone occurrence': get_cycfreq,
    'Probability of temperatures below the 30-percentile': get_prob_cold,
    'Probability of temperatures above the 70-percentile': get_prob_warm,
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
        'all': ['prob_t850', 'cycfreqa', 'mtafreqa', ],
        'test': [],
        'website_only': [],  # do not plot anything, only refresh website
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
                data[plev,q] = get_special[q](fc_str, fc_str_prev, plev, q, static)
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
    
    fclist = [forecast - td(day) for day in range(21)]
    leadlist = list(range(0,841,12))
    leadlist_link = [24*(week*7 + day) for week in range(5) for day in [0,2,4]] + [840,]

    render_webpage('npolar', 'ec_ext', forecast, fclist, leadlist, leadlist_link)
    render_webpage('spolar', 'ec_ext', forecast, fclist, leadlist, leadlist_link)

# the end
