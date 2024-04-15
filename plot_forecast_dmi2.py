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


u10 = 165
v10 = 166
q_map = {
    '2m Temperature': 167,
    '2m Relative humidity': 260242,
    '10m U-wind component': u10,
    '10m V-wind component': v10,
    '10m Wind gusts': 260065,
    '10m Wind barbs': (u10, v10),
    'Cloud base altitude': 260107,
    'Sensible heat flux': 260003,
    'Latent heat flux': 260002,
    'Sea-surface temperature': {'paramId': 130, 'typeOfLevel': 'heightAboveGround', 'level': 0},  # is actually a generic surface temperature
    'Land-sea mask': 260179,
    'Sea-level pressure': {'paramId': 54, 'typeOfLevel': 'heightAboveSea', 'level': 0},
    'Total precipitation': 228228,
    'Temperature': 130,
    'Relative humidity': 157,
    'Wind barbs': (131, 132),
}

pconf[None,'2m Relative humidity','hook'] = lambda rh: rh/100.0 # from % to 1


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
        if type(q) == dict:
            msgs = fsfc.select(**q)
        else:
            msgs = fsfc.select(paramId=q)

    # Standard pressure levels
    else:
        plev = int(plev)
        msgs = fpl.select(paramId=q, typeOfLevel='isobaricInhPa', level=plev)

    _assure_unique(msgs, plev, q)

    dat = msgs[0].values 

    # Aggregated surface variables
    if plev == 'sfc':
        if q in [228228,260002,260003]:
            prevavail = False
            if q in agg_last:
                tmp = agg_last[q]
                prevavail = True
            
            agg_last[q] = dat.copy()
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

def get_q(fpl, fsfc, level, var):
    # Only relative humidity available on pressure levels
    plev = level2plev(level)

    rh = get_single(fpl, fsfc, plev, q_map['Relative humidity'])
    t = get_single(fpl, fsfc, plev, q_map['Temperature'])
    
    e = dynlib.thermodyn.e_from_rh(rh[np.newaxis,:,:], t[np.newaxis,:,:])
    pres = np.ones(e.shape) * float(plev) * 100
    q = dynlib.thermodyn.q_from_e(e, pres)

    return q[0,:,:]

def get_ff10(fpl, fsfc, level, var):
    plev = level2plev(level)

    u10 = get_single(fpl, fsfc, plev, q_map['10m U-wind component'])
    v10 = get_single(fpl, fsfc, plev, q_map['10m V-wind component'])

    return np.sqrt(u10*u10 + v10*v10)

def get_caoidx(fpl, fsfc, level, var):
    t = get_single(fpl, fsfc, '850', q_map['Temperature'])
    msl = get_single(fpl, fsfc, 'sfc', q_map['Sea-level pressure'])
    sst = get_single(fpl, fsfc, 'sfc', q_map['Sea-surface temperature'])
    siconc = get_siconc(fpl, fsfc, level, var)
    landmask = get_single(fpl, fsfc, 'sfc', q_map['Land-sea mask'])

    CAOi = dynlib.detect.cold_air_outbreak_index(t[np.newaxis,:,:], msl[np.newaxis,:,:], sst[np.newaxis,:,:], siconc[np.newaxis,:,:], landmask)[0,:,:]
    CAOi[np.isnan(CAOi)] = 0.0

    return CAOi

def get_shf(fpl, fsfc, level, var):
    sshf = get_single(fpl, fsfc, 'sfc', q_map['Sensible heat flux'])
    slhf = get_single(fpl, fsfc, 'sfc', q_map['Latent heat flux'])
    
    return (sshf + slhf)/-3600.0 # from J/h to W, and make according to our sign convention

get_special = {
    'Sea ice concentration': get_siconc,
    'Specific humidity': get_q,
    '10m Wind speed': get_ff10,
    'Cold-air outbreak index': get_caoidx,
    'Surface total heat flux': get_shf,
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
    conf.datapath.insert(0, '/share/base/dmi2')
    
    leadlist = list(range(0,61,3))
    leadlist_link = range(0,61,6)

    DATEFMT_FNAME = '%Y-%m-%dT%H%M%SZ'
    for lead in leadlist:
        # Save expensive intermediate steps to avoid recalculation
        CACHE = {}

        date = forecast + lead * td(0,3600)
        
        initstr = forecast.strftime(DATEFMT_FNAME)
        validstr = date.strftime(DATEFMT_FNAME)
        fpath_pl = conf.datapath[0] + f'/{fc_str}/HARMONIE_DINI_PL_{initstr}_{validstr}.grib'
        fpath_sfc = conf.datapath[0] + f'/{fc_str}/HARMONIE_DINI_SF_{initstr}_{validstr}.grib'
        print(fpath_pl)

        fpl = pygrib.open(fpath_pl)
        fsfc = pygrib.open(fpath_sfc)

        static = grid_by_latlon(*fpl[1].latlons())
        static.oro = np.zeros((static.ny, static.nx))
        static.t_parsed = [date, ]
        static.prepare_rotation()
        
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
