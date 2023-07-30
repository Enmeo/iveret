#!/usr/bin/env python
# -*- encoding: utf-8

import copy
import pygrib

import matplotlib as mpl
mpl.use('Agg')
import scipy.interpolate as interp

from plotconfig import *
from settings.common2 import *

from dynlib.gridlib import grid_by_latlon
import dynlib.diag
import dynlib.detect
import dynlib.thermodyn
import dynlib.sphere
import dynlib.utils

from current_fc_dmi import get_current_fc_dmi as get_current_fc


q_map = {
    '2m Temperature': {'indicatorOfParameter': 11, 'typeOfLevel': 'heightAboveGround', 'level': 2},
    '2m Relative humidity': {'indicatorOfParameter': 52, 'typeOfLevel': 'heightAboveGround', 'level': 2},
    'Sea-level pressure': {'indicatorOfParameter': 1, 'typeOfLevel': 'heightAboveSea', 'level': 0},
    'Total precipitation': {'indicatorOfParameter': 61},
    'Temperature': 11,
}


def _assure_unique(msgs, plev, q):
    if len(msgs) > 1:
        for msg in msgs:
            print(msg)
        raise ValueError('Found multiple grib messages fitting (%s, %s)' % (q, plev))
    elif len(msgs) < 1:
        raise ValueError('Found no grib messages fitting (%s, %s)' % (q, plev))

    return


agg_last = {}
def get_single(fpl, fsfc, plev, q):
   # Standard surface variables
    if plev == 'sfc':
        msgs = fsfc.select(**q)

    # Standard pressure levels
    else:
        plev = int(plev)
        msgs = fpl.select(indicatorOfParameter=q, typeOfLevel='isobaricInhPa', level=plev)

    _assure_unique(msgs, plev, q)

    dat = msgs[0].values 

    # Aggregated surface variables
    if plev == 'sfc':
        param_id = q['indicatorOfParameter']
        if param_id in [61, ]:
            prevavail = False
            if param_id in agg_last:
                tmp = agg_last[param_id]
                prevavail = True
            
            agg_last[param_id] = dat.copy()
            if prevavail:
                dat -= tmp

            # From 3-hourly sums to mean per hour
            dat /= 3

    return dat


def get(fpl, fsfc, level, var):
    plev = level2plev(level)
    if var in q_map:
        q = q_map[var]
    else:
        raise ValueError(f'Unknown variable `{var}`.')

    if type(q) in [int, dict]:
        dat = get_single(fpl, fsfc, plev, q)
    else:
        dat = tuple([])
        for q_single in q:
            dat += (get_single(fpl, fsfc, plev, q_single), )

    return dat


def get_siconc(fpl, fsfc, level, var):
    # Not part of the available variable set.
    return np.zeros(fsfc[1].values.shape)

get_special = {
    'Sea ice concentration': get_siconc,
}


# -----------------------------------------------------------------------------

if __name__ == '__main__':
    import sys

    # Most recent available data
    forecast = get_current_fc()
    
    # Override
    #forecast = dt(2019,8,27,18)
    plot_only_init = False
    
    print('Plotting the DMI %s forecasts' % forecast.strftime('%Y-%m-%d %H'))

    plots = [plotter(domainname, domains[domainname], 'dmi', plotname, plot)
            for domainname, plots_by_domain in plots['dmi'].items() for plotname, plot in plots_by_domain.items()]

    print(len(plots))
    
    fc_str = forecast.strftime('%Y%m%d%H')
    conf.datapath.insert(0, '/share/base/dmi')
    
    leadlist = list(range(0,55,3))
    leadlist_link = range(0,55,6)

    DATEFMT_FNAME = '%Y-%m-%dT%H%M%SZ'
    for lead in leadlist:
        # Save expensive intermediate steps to avoid recalculation
        CACHE = {}

        date = forecast + lead * td(0,3600)
        
        initstr = forecast.strftime(DATEFMT_FNAME)
        validstr = date.strftime(DATEFMT_FNAME)
        fpath_pl = conf.datapath[0] + f'/{fc_str}/HARMONIE_NEA_PL_{initstr}_{validstr}.grib'
        fpath_sfc = conf.datapath[0] + f'/{fc_str}/HARMONIE_NEA_SF_{initstr}_{validstr}.grib'
        print(fpath_pl)

        fpl = pygrib.open(fpath_pl)
        fsfc = pygrib.open(fpath_sfc)

        static = grid_by_latlon(*fpl[1].latlons())
        static.oro = np.zeros((static.ny, static.nx))
        static.t_parsed = [date, ]
        
        data_inst = {}
        for plot in plots:
            for plev, q in plot.requires:
                if (plev,q) in data_inst:
                    continue

                if q in get_special:
                    data_inst[plev,q] = get_special[q](fpl, fsfc, plev, q)
                else:
                    data_inst[plev,q] = get(fpl, fsfc, plev, q)
    
        for plot in plots:
            plot.plot(data_inst, static, forecast, date)
            plt.close()


    print('Creating page for forecasts from %s.' % forecast.strftime('%d.%m.%Y, %H UTC'))

    fclist = [forecast - td(0.25)*i for i in range(29)]
    render_webpage('vestland', 'dmi', forecast, fclist, leadlist, leadlist_link)
    render_webpage('snorway', 'dmi', forecast, fclist, leadlist, leadlist_link)
    render_webpage('dmi', 'dmi', forecast, fclist, leadlist, leadlist_link)

# the end
