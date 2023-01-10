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

from current_fc_gfs import get_current_fc_gfs as get_current_fc


q_map = {
    'U component of wind': 'U component of wind',
    'V component of wind': 'V component of wind',
    'Temperature': 'Temperature',
    'Sea-level pressure': 'MSLP (Eta model reduction)',
    'Wind barbs': ('U component of wind', 'V component of wind'),
    '10m Wind barbs': ('10 metre U wind component', '10 metre V wind component'),
    '10m Wind gusts': 'Wind speed (gust)',
    'Convective precipitation': 'Convective precipitation rate',
    'Large-scale precipitation': 'Precipitation rate',
    'Total column water vapour': 'Precipitable water',
    'Surface sensible heat flux': 'Sensible heat net flux',
    'Surface latent heat flux': 'Latent heat net flux',
}


def _assure_unique(msgs, plev, q):
    if len(msgs) > 1:
        raise ValueError('Found multiple grib messages fitting (%s, %s)' % (q, plev))
    elif len(msgs) < 1:
        raise ValueError('Found no grib messages fitting (%s, %s)' % (q, plev))

    return


def get_single(f, plev, q):
    #print(plev, q)

    # Standard tropopause-level variables
    if plev == 'pv2000':
        msgs = f.select(name=q, typeOfLevel='tropopause')
    
    # Aggregated surface variables
    elif plev == 'sfc' and q in ['Convective precipitation rate', 'Precipitation rate', 'Sensible heat net flux', 'Latent heat net flux', ]:
        if f[1].forecastTime == 0:
            return np.zeros(f[1].values.shape)
        msgs = f.select(name=q, typeOfLevel='surface', stepType='avg')

    # Standard surface variables
    elif plev == 'sfc':
        msgs = f.select(name=q)

    # Standard pressure levels
    else:
        plev = int(plev)
        msgs = f.select(name=q, typeOfLevel='isobaricInhPa', level=plev)

    _assure_unique(msgs, plev, q)
    
    return msgs[0].values


def get(f, level, var):
    plev = level2plev(level)
    if var in q_map:
        q = q_map[var]
    else:
        raise ValueError(f'Unknown variable `{var}`.')

    if type(q) == str:
        dat = get_single(f, plev, q)
    else:
        dat = tuple([])
        for q_single in q:
            dat += (get_single(f, plev, q_single), )

    return dat

def get_pt(f, level, var):
    plev = level2plev(level)
    t = get_single(f, plev, 'Temperature')[np.newaxis,:,:]
    if level[-3:] == 'hPa':
        p = np.ones((1,1,1)) * plev*100
        return dynlib.thermodyn.theta_from_temp(t, p)[0,:,:]
    else:
        p = get_single(f, plev, 'Pressure')[np.newaxis,:,:]
        return dynlib.thermodyn.theta_from_temp(t, p)[0,:,:]

def get_eqpt(f, level, var):
    plev = level2plev(level)
    t = get_single(f, plev, 'Temperature')[np.newaxis,:,:]
    q = get_single(f, plev, 'Specific humidity')[np.newaxis,:,:]
    p = np.ones(t.shape) * int(plev)*100

    return dynlib.thermodyn.thetae_from_q(q, t, p)[0,:,:]


def get_z(f, level, var):
    plev = level2plev(level)
    z = get_single(f, plev, 'Geopotential Height')

    return z*9.81

def get_ff(f, level, var):
    plev = level2plev(level)
    u = get_single(f, plev, 'U component of wind')
    v = get_single(f, plev, 'V component of wind')

    return np.sqrt(u**2 + v**2)

def get_ff10(f, level, var):
    u10 = get_single(f, 'sfc', '10 metre U wind component')
    v10 = get_single(f, 'sfc', '10 metre V wind component')

    return np.sqrt(u10**2 + v10**2)

def get_cao(f, level, var):
    t = get_single(f, '850', 'Temperature')
    msl = get_single(f, 'sfc', 'MSLP (Eta model reduction)')
    msgs = f.select(name='Temperature', typeOfLevel='surface')
    sst = msgs[0].values
    siconc = get_single(f, 'sfc', 'Sea ice area fraction')
    landmask = get_single(f, 'sfc', 'Land-sea mask')

    CAOi = dynlib.detect.cold_air_outbreak_index(t[np.newaxis,:,:], msl[np.newaxis,:,:], sst[np.newaxis,:,:], siconc[np.newaxis,:,:], landmask)[0,:,:]
    CAOi[np.isnan(CAOi)] = 0.0

    return CAOi

def get_cc(f, level, var):
    if f[1].forecastTime == 0:
        return np.zeros(f[1].values.shape)
    elif var == 'Low cloud cover':
        msgs = f.select(typeOfFirstFixedSurface='214', stepType='instant')
    elif var == 'Mid-level cloud cover':
        msgs = f.select(typeOfFirstFixedSurface='224', stepType='instant')
    elif var == 'High cloud cover':
        msgs = f.select(typeOfFirstFixedSurface='234', stepType='instant')
    else:
        raise ValueError(f'get_cc cannot get variable `{var}`.')

    _assure_unique(msgs, plev, q)

    return msgs[0].values / 100 # Convert from percent to 1, as this is expected in the general plot definition

def get_tp(f, level, var):
    lsp = get_single(f, 'sfc', 'Precipitation rate')
    cp = get_single(f, 'sfc', 'Convective precipitation rate')

    return (lsp+cp) * 3600 # Homogenise units with the other fc sources to mm/h

def get_siconc(f, level, var):
    msgs = f.select(name='Sea ice area fraction', typeOfLevel='surface')
    vals = msgs[0].values
    msgs = f.select(name='Land-sea mask')
    landmask = msgs[0].values
    vals[landmask == 1] = np.nan

    return vals

def get_sst(f, level, var):
    msgs = f.select(name='Temperature', typeOfLevel='surface')
    vals = msgs[0].values
    msgs = f.select(name='Land-sea mask')
    landmask = msgs[0].values
    vals[landmask == 1] = np.nan

    return vals

def get_rr(f, level, var):
    rr = get_single(f, 'sfc', q_map[var])

    return rr * 3600 # Homogenise units with the other fc sources to mm/h

def get_cape(f, level, var):
    msgs = f.select(name='Convective available potential energy', typeOfLevel='surface', level=0)

    _assure_unique(msgs, plev, q)

    return msgs[0].values

def cache_iwvt_components(f):
    plevs = ['200', '250', '300', '350', '400', '450', '500', '550', '600', '650',
            '700', '750', '800', '850', '900', '925', '950', '975', '1000']
    wgts = [25, 50, 50, 50, 50, 50, 50, 50, 50, 50, 
            50, 50, 50, 50, 37.5, 25, 25, 25, 12.5]
    
    q = get_single(f, plevs[0], 'Specific humidity')
    u = get_single(f, plevs[0], 'U component of wind')
    v = get_single(f, plevs[0], 'V component of wind')
    CACHE['viewvt'] = q*u*wgts[0]
    CACHE['vinwvt'] = q*v*wgts[0]
    for plev, wgt in zip(plevs[1:], wgts[1:]):
        q = get_single(f, plev, 'Specific humidity')
        u = get_single(f, plev, 'U component of wind')
        v = get_single(f, plev, 'V component of wind')
        CACHE['viewvt'] += q*u*wgt
        CACHE['vinwvt'] += q*v*wgt

    CACHE['viewvt'] *= 100/9.81
    CACHE['vinwvt'] *= 100/9.81

    # Interpolation to T84 resolution
    u, conv = dynlib.utils.fill_nan(CACHE['viewvt'][np.newaxis,:,:])
    v, conv = dynlib.utils.fill_nan(CACHE['vinwvt'][np.newaxis,:,:])
    br, bi, cr, ci = dynlib.sphere.sh_analysis_vector(u, v)
    dynlib.sphere.trunc_triangular(br, bi, 84)
    dynlib.sphere.trunc_triangular(cr, ci, 84)
    u, v = dynlib.sphere.sh_synthesis_vector(u.shape[2], br,bi,cr,ci)

    CACHE['viewvt_smooth'], CACHE['vinwvt_smooth'] = u[0,:,:], v[0,:,:]

    return

def get_iwvt_vector(f, level, var):
    if not 'viewvt' in CACHE:
        cache_iwvt_components(f)

    return CACHE['viewvt'], CACHE['vinwvt']

def get_absiwvt(f, level, var):
    if not 'viewvt' in CACHE:
        cache_iwvt_components(f)

    return np.sqrt(CACHE['viewvt']**2 + CACHE['vinwvt']**2)

def get_iwvt_axis(f, level, var):
    if not 'viewvt_smooth' in CACHE:
        cache_iwvt_components(f)

    dynfor.config.nsmooth = 0
    dynfor.config.minlen = 2.0e6
    dynfor.config.jetint_thres = 5.0e-7
    dynfor.config.searchrad = 1.5
    dynfor.config.grid_cyclic_ew = True

    # Integrated water vapour transport axis detections
    u, v = CACHE['viewvt_smooth'][np.newaxis,:,:], CACHE['vinwvt_smooth'][np.newaxis,:,:]
    iwvta, iwvtoff = dynlib.detect.jetaxis(10000, 2000, u, v, static.dx, static.dy)
    iwvta = iwvta[0,:,:]
    iwvtoff = iwvtoff[0,:].astype('i4')

    return iwvta, iwvtoff


PERC_PATH = '/home/ubuntu/data'
PERC_PERIOD = '1979-2020'
conf.datapath.insert(1, PERC_PATH)
def get_t_ano(f, level, var):
    plev = level2plev(level)
    t = get_single(f, plev, 'Temperature')

    filename = 'ea.ans.%s.%s.t_percs' % (PERC_PERIOD, plev)
    print('Using base data from %s' % filename)
    f, perc_data = metopen(filename, 't', no_static=True)
    perc_data = np.roll(perc_data, perc_data.shape[3]//2, axis=3) # GFS grid is from 0 to 360E, not -180 to 180E
    percs = f.variables['percentile'][:]
    f.close()
    
    # Current month (index, starting with January as 0)
    mon = static.t_parsed[0].month - 1
    
    # Calculate anomalies compared to median
    idx = np.argwhere(percs == 0.5)[0,0]
    return t - perc_data[mon,idx]


def get_t_perc(f, level, var):
    plev = level2plev(level)
    t = get_single(f, plev, 'Temperature')

    filename = 'ea.ans.%s.%s.t_percs' % (PERC_PERIOD, plev)
    print('Using base data from %s' % filename)
    f, perc_data = metopen(filename, 't', no_static=True)
    perc_data = np.roll(perc_data, perc_data.shape[3]//2, axis=3) # GFS grid is from 0 to 360E, not -180 to 180E
    percs = f.variables['percentile'][:]
    f.close()
    
    # Current month (index, starting with January as 0)
    mon = static.t_parsed[0].month - 1
    
    # Find percentiles
    t_perc = np.empty(t.shape, dtype='i1') * np.nan
    mask = t < perc_data[mon,0]
    t_perc[mask] = 0
    for i in range(1, perc_data.shape[1]):
        dmin = perc_data[mon,i-1]
        dmax = perc_data[mon,i]
        mask = np.logical_and(t >= dmin, t < dmax)
        t_perc[mask] = i
    i += 1
    mask = t >= perc_data[mon,-1]
    t_perc[mask] = i

    return t_perc


def get_frovo(f, level, var):
    LEVELS = ['700 hPa', '850 hPa', '925 hPa', ]
    
    eqpt_ = get_eqpt(f, LEVELS[0], var)[np.newaxis,:,:]
    s = eqpt_.shape
    s = s[:1] + (len(LEVELS), ) + s[1:]
    eqpt = np.empty(s)
    eqpt[:,0,:,:] = eqpt_
    for pidx, level in zip(range(1,len(LEVELS)), LEVELS[1:]):
        eqpt[:,pidx,:,:] = get_eqpt(f, level, var)[np.newaxis,:,:]

    dynfor.config.nsmooth = 10
    dynfor.config.tfp_mingrad_largescale = 3.75e-5
    dynfor.config.tfp_mingrad_smallscale = 5.25e-5
    dynfor.config.minsize = 75000.0e6

    frovo = dynlib.detect.frontalvolume_smallscale(eqpt, static.dx, static.dy)
    frovo = frovo[0,1,:,:]
    frovo[frovo > 0.5] = 1.0

    return frovo


def get_frontogenesis(f, level, var):
    plev = level2plev(level)
    u = get_single(f, plev, 'U component of wind')[np.newaxis,np.newaxis,:,:]
    v = get_single(f, plev, 'V component of wind')[np.newaxis,np.newaxis,:,:]
    eqpt = get_eqpt(f, level, var)
    eqpt = dynlib.utils.smooth_xy(eqpt[np.newaxis,:,:], 3)[:,np.newaxis,:,:]

    w = np.zeros(u.shape)
    heat = np.zeros(u.shape)
    dz = np.ones(u.shape)

    frdiv, frdef, frtilt, frheat = dynlib.diag.frontogenesis_contributors(u, v, w, eqpt, heat, static.dx, static.dy, dz)

    return (frdef + frdiv).squeeze() * 1.0e5 # Convert to K/(100 km)/s


def get_T84_ff(f, level, var):
    if (level, 'u_smooth') in CACHE:
        return np.sqrt(CACHE[level,'u_smooth']**2 + CACHE[level,'v_smooth']**2)[0,:,:]

    plev = level2plev(level)
    u = get_single(f, plev, 'U component of wind')[np.newaxis,:,:]
    v = get_single(f, plev, 'V component of wind')[np.newaxis,:,:]

    # Filtering to T84 resolution
    u, conv = dynlib.utils.fill_nan(u)
    v, conv = dynlib.utils.fill_nan(v)
    br, bi, cr, ci = dynlib.sphere.sh_analysis_vector(u, v)
    dynlib.sphere.trunc_triangular(br, bi, 84)
    dynlib.sphere.trunc_triangular(cr, ci, 84)
    u, v = dynlib.sphere.sh_synthesis_vector(u.shape[2], br,bi,cr,ci)

    CACHE[level,'u_smooth'] = u
    CACHE[level,'v_smooth'] = v

    return np.sqrt(u**2 + v**2)[0,:,:]


# Helpers for get_jetaxis
def _interpolate_location(dat, lat, lon, grid):
    ''' Interpolate dat to the jet locations (using the coordinates of its points) '''

    dati = np.empty(lat.shape[:2])
    func = interp.RectBivariateSpline(grid.y[::-1,0], grid.x[0,:], dat[::-1,:], kx=1, ky=1)
    dati[:] = func(lat[:], lon[:], grid=False)

    return dati

# For ERAi and ERA5 and global forecasts
def _idx2latlon(jetaxis):
    lon = (jetaxis[:,0]-1) * 0.5 - 180
    lat = 90.0 - (jetaxis[:,1]-1) * 0.5

    return lat, lon

def get_jetaxis(f, level, var):
    dynfor.config.nsmooth = 0
    dynfor.config.minlen = 2.0e6
    dynfor.config.jetint_thres = 0.55e-8
    dynfor.config.searchrad = 1.5
    
    if not (level,'u_smooth') in CACHE:
        get_T84_ff(f, level, var)
    
    # Jet axis detections
    ja, jaoff = dynlib.detect.jetaxis(10000, 10000, CACHE[level,'u_smooth'], CACHE[level,'v_smooth'], static.dx, static.dy)
    ja = ja[0,:,:]
    jaoff = jaoff[0,:].astype('i4')

    # Interpolate potential temperature to jet positions
    pt = get_pt(f, level, 'Potential temperature')
    lat, lon = _idx2latlon(ja)
    pti = _interpolate_location(pt, lat, lon, static)
    ja = np.concatenate((ja, pti[:,np.newaxis]), axis=1)

    return ja, jaoff


def get_rh2m(f, level, var):
    rh2m = get_single(f, 'sfc', '2 metre relative humidity')

    return rh2m / 100.0 # Convert from percent to 1

get_special = {
    'Potential temperature': get_pt,
    'Equivalent potential temperature': get_eqpt,
    'Geopotential': get_z,
    'Wind speed': get_ff,
    '10m Wind speed': get_ff10,
    'Cold-air outbreak index': get_cao,
    'Low cloud cover': get_cc,
    'Mid-level cloud cover': get_cc,
    'High cloud cover': get_cc,
    'Total precipitation': get_tp,
    'Sea-surface temperature': get_sst,
    'Sea ice concentration': get_siconc,
    'Convective precipitation': get_rr,
    'Large-scale precipitation': get_rr,
    'Convective available potential energy': get_cape,
    'Column integral water vapour transport vector': get_iwvt_vector,
    'Column integral water vapour transport': get_absiwvt,
    'Moisture transport axes': get_iwvt_axis,
    'Temperature anomaly': get_t_ano,
    'Temperature percentiles': get_t_perc,
    'Frontal volumes': get_frovo,
    'Frontogenesis': get_frontogenesis,
    'Jet axes': get_jetaxis,
    'Wind speed filtered to T84': get_T84_ff,
    '2m Relative humidity': get_rh2m,
}


# -----------------------------------------------------------------------------

if __name__ == '__main__':
    import sys

    # Most recent available data
    forecast = get_current_fc()
    
    # Override
    #forecast = dt(2019,8,27,18)
    plot_only_init = False
    
    print('Plotting the GFS %s forecasts' % forecast.strftime('%Y-%m-%d %H'))

    PLOT_SETS = {
        'plev': ['z500_msl', 't850_msl', 'eqpt850_cape', 'tcwv', 'iwvt_axis', 't850_perc', ],
        'pv2': ['ptpv2_jets', ],
        'test': [],
        'sfc': ['tcc', 'ff10_gusts', 'cao_winds', 'sshf_winds', 'slhf_winds', 'rh2m_tp', ],
    }
    
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg in PLOT_SETS:
                plots = [plotter(domainname, domains[domainname], 'noaa', plotname, plot)
                    for domainname, plots_by_domain in plots['noaa'].items() for plotname, plot in plots_by_domain.items()
                    if plotname in PLOT_SETS[arg]
                ]
                print('Plotting plot set "%s".' % arg)
            else:
                raise ValueError('Unknown plot set "%s".' % arg)
    else:
        plots = [plotter(domainname, domains[domainname], 'noaa', plotname, plot)
            for domainname, plots_by_domain in plots['noaa'].items() for plotname, plot in plots_by_domain.items()]

        print('No plot set specified, plotting all plot sets.')

    print(len(plots))
    
    fc_str = forecast.strftime('%Y%m%d%H')
    conf.datapath.insert(0, '/share/base/noaa')
    
    leadlist = list(range(0,72,3))
    leadlist.extend(range(72,241,6))
    leadlist_link = range(0,241,12)

    for lead in leadlist:
        # Save expensive intermediate steps to avoid recalculation
        CACHE = {}

        date = forecast + lead * td(0,3600)
        
        fpath = conf.datapath[0] + f'/{fc_str}/gfs.t{forecast.hour:02d}z.pgrb2.0p50.f{lead:03d}'
        print(fpath)
        f = pygrib.open(fpath)
        static = grid_by_latlon(*f[1].latlons())
        static.oro = np.zeros((static.ny, static.nx))
        static.t_parsed = [date, ]
        
        data_inst = {}
        for plot in plots:
            for plev, q in plot.requires:
                if (plev,q) in data_inst:
                    continue

                if q in get_special:
                    data_inst[plev,q] = get_special[q](f, plev, q)
                else:
                    data_inst[plev,q] = get(f, plev, q)
    

        #for q,plev in data_inst:
        #    data_inst[q,plev] = data_inst[q,plev].squeeze()
        
        for plot in plots:
            plot.plot(data_inst, static, forecast, date)
            plt.close()


    print('Creating page for forecasts from %s.' % forecast.strftime('%d.%m.%Y, %H UTC'))

    fclist = [forecast - td(0.25)*i for i in range(31)]
    render_webpage('natl', 'noaa', forecast, fclist, leadlist, leadlist_link)
    render_webpage('npolar', 'noaa', forecast, fclist, leadlist, leadlist_link)
    render_webpage('spolar', 'noaa', forecast, fclist, leadlist, leadlist_link)

# the end
