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

from current_fc import get_current_fc



q_map = {
    '2m Temperature': 't2m',
    'Cloud base altitude': 'clba',
    'Temperature': 't',
    'Potential temperature': 'pt',
    'Specific humidity': 'q',
    'Sea-level pressure': 'msl',
    'Convective precipitation': 'cp',
    'Large-scale precipitation': 'lsp',
    'Convective available potential energy': 'cape',
    'Total column water vapour': 'tcwv',
    '10m Wind barbs': ('u10', 'v10'),
    '10m Wind gusts': 'fg10',
    'Wind barbs': ('u', 'v'),
    'Vertical wind': 'w',
    'Geopotential': 'z',
    'Potential vorticity': 'pv',
    'Column integral water vapour transport vector': ('viewvt', 'vinwvt'),
    'Low cloud cover': 'lcc',
    'Mid-level cloud cover': 'mcc',
    'High cloud cover': 'hcc',
}

qf = {
    'viewvt': 'viwve',
    'vinwvt': 'viwvn',
}


# Save expensive intermediate steps to avoid recalculation
CACHE = {}


def get_single(fc_str, plev, q):
    fname = f'{fc_str}/ec.for.{fc_str}.{plev}.{q}'
    try:
        f, dat, static = metopen(fname, qf.get(q, q))
        dat = dat.squeeze()
        if plev in mask:
            dat[mask[plev]] = np.nan
    except Exception as e:
        print(type(e), e)
        dat = None

    return dat


def get_single_ens(fc_str, plev, q):
    fname = f'{fc_str}/ec.ens.{fc_str}.{plev}.{q}'
    try:
        f, dat, static = metopen(fname, qf.get(q, q))
        dat = dat.squeeze()
        if plev in mask:
            dat[mask[plev]] = np.nan
    except Exception as e:
        print(type(e), e)
        dat = None

    return dat


def get_single_ensctrl(fc_str, plev, q):
    fname = f'{fc_str}/ec.ensctrl.{fc_str}.{plev}.{q}'
    try:
        f, dat, static = metopen(fname, qf.get(q, q))
        dat = dat.squeeze()
        if plev in mask:
            dat[mask[plev]] = np.nan
    except Exception as e:
        print(type(e), e)
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


landmask = np.load(VAERKART_ROOT+'/settings/ecmwf_fc_sea_mask.npy')
def mask_land(data):
    data[:,landmask] = np.nan

    return data


def get_eqpt(fc_str, level, var):
    plev = level2plev(level)
    t = get_single(fc_str, plev, 't')
    q = get_single(fc_str, plev, 'q')
    p = np.ones(t.shape) * int(plev)*100

    return dynlib.thermodyn.thetae_from_q(q, t, p)


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

    CAOi = dynlib.detect.cold_air_outbreak_index(t, msl, sst, siconc, landmask)
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

def get_lsp(fc_str, level, var):
    lsp = get_single(fc_str, 'sfc', 'lsp')

    return _normalize_cumulates(lsp*1000*3600)

def get_cp(fc_str, level, var):
    cp = get_single(fc_str, 'sfc', 'cp')

    return _normalize_cumulates(cp*1000*3600)

def get_sshf(fc_str, level, var):
    sshf = get_single(fc_str, 'sfc', 'sshf')

    return _normalize_cumulates(-sshf)

def get_slhf(fc_str, level, var):
    slhf = get_single(fc_str, 'sfc', 'slhf')

    return _normalize_cumulates(-slhf)

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


def get_absiwvt(fc_str, level, var):
    u = get_single(fc_str, 'sfc', 'viewvt')
    v = get_single(fc_str, 'sfc', 'vinwvt')

    ff = np.sqrt(u**2 + v**2)

    return ff


def get_iwvt_axis(fc_str, level, var):
    if ('sfc', 'viewvt_smooth') in CACHE:
        u = CACHE['sfc','viewvt_smooth']
        v = CACHE['sfc','vinwvt_smooth']

    else:
        u = get_single(fc_str, 'sfc', 'viewvt')
        v = get_single(fc_str, 'sfc', 'vinwvt')

        # Interpolation to T84 resolution
        u, conv = dynlib.utils.fill_nan(u)
        v, conv = dynlib.utils.fill_nan(v)
        br, bi, cr, ci = dynlib.sphere.sh_analysis_vector(u, v)
        dynlib.sphere.trunc_triangular(br, bi, 84)
        dynlib.sphere.trunc_triangular(cr, ci, 84)
        u, v = dynlib.sphere.sh_synthesis_vector(u.shape[2], br,bi,cr,ci)
        CACHE['sfc','viewvt_smooth'] = u
        CACHE['sfc','vinwvt_smooth'] = v

    dynfor.config.nsmooth = 0
    dynfor.config.minlen = 1.5e6
    dynfor.config.jetint_thres = 5.0e-7
    dynfor.config.searchrad = 1.5
    dynfor.config.grid_cyclic_ew = True

    # Integrated water vapour transport axis detections
    iwvta, iwvtoff = dynlib.detect.jetaxis(10000, 2000, u, v, static.dx, static.dy)
    iwvtoff = iwvtoff.astype('i4')

    return iwvta, iwvtoff


__, tcwv_clim = metopen('settings/ea.ans.1979-2020.sfc.tcwv.zonaltimeavg', 'tcwv', no_static=True)
tcwv_clim = np.maximum(tcwv_clim, 5)
def get_iwvta_axis(fc_str, level, var):
    if ('sfc', 'viewvt_smooth') in CACHE:
        u = CACHE['sfc','viewvt_smooth'].copy()
        v = CACHE['sfc','vinwvt_smooth'].copy()

    else:
        u = get_single(fc_str, 'sfc', 'viewvt')
        v = get_single(fc_str, 'sfc', 'vinwvt')

        # Interpolation to T84 resolution
        u, conv = dynlib.utils.fill_nan(u)
        v, conv = dynlib.utils.fill_nan(v)
        br, bi, cr, ci = dynlib.sphere.sh_analysis_vector(u, v)
        dynlib.sphere.trunc_triangular(br, bi, 84)
        dynlib.sphere.trunc_triangular(cr, ci, 84)
        u, v = dynlib.sphere.sh_synthesis_vector(u.shape[2], br,bi,cr,ci)
        CACHE['sfc','viewvt_smooth'] = u.copy()
        CACHE['sfc','vinwvt_smooth'] = v.copy()

    u /= tcwv_clim[np.newaxis,:,np.newaxis]
    v /= tcwv_clim[np.newaxis,:,np.newaxis]

    dynfor.config.nsmooth = 0
    dynfor.config.minlen = 1.5e6
    dynfor.config.jetint_thres = 3.5e-7 / 15.0**2 # climatological TCWV at around 45 degN/S
    dynfor.config.searchrad = 1.5
    dynfor.config.grid_cyclic_ew = True

    # Integrated water vapour transport axis detections
    iwvta, iwvtoff = dynlib.detect.jetaxis(10000, 2000, u, v, static.dx, static.dy)
    iwvtoff = iwvtoff.astype('i4')

    return iwvta, iwvtoff


PERC_PATH = '/home/ubuntu/data'
PERC_PERIOD = '1979-2020'
conf.datapath.insert(1, PERC_PATH)
def get_t_ano(fc_str, level, var):
    plev = level2plev(level)
    t = get_single(fc_str, plev, 't')

    filename = 'ea.ans.%s.%s.t_percs' % (PERC_PERIOD, plev)
    print('Using base data from %s' % filename)
    f, perc_data = metopen(filename, 't', no_static=True)
    percs = f.variables['percentile'][:]
    f.close()
    
    # Current month (index, starting with January as 0)
    mon = static.t_parsed[0].month - 1
    
    # Calculate anomalies compared to median
    idx = np.argwhere(percs == 0.5)[0,0]
    return t - perc_data[np.newaxis,mon,idx]


def get_t_perc(fc_str, level, var):
    plev = level2plev(level)
    t = get_single(fc_str, plev, 't')

    filename = 'ea.ans.%s.%s.t_percs' % (PERC_PERIOD, plev)
    print('Using base data from %s' % filename)
    f, perc_data = metopen(filename, 't', no_static=True)
    percs = f.variables['percentile'][:]
    f.close()
    
    # Current month (index, starting with January as 0)
    mon = static.t_parsed[0].month - 1
    
    # Find percentiles
    t_perc = np.empty(t.shape, dtype='i1') * np.nan
    mask = t < perc_data[mon,0][np.newaxis,:,:]
    t_perc[mask] = 0
    for i in range(1, perc_data.shape[1]):
        dmin = perc_data[mon,i-1][np.newaxis,:,:]
        dmax = perc_data[mon,i][np.newaxis,:,:]
        mask = np.logical_and(t >= dmin, t < dmax)
        t_perc[mask] = i
    i += 1
    mask = t >= perc_data[mon,-1][np.newaxis,:,:]
    t_perc[mask] = i

    return t_perc


def get_frovo(fc_str, level, var):
    LEVELS = ['700 hPa', '850 hPa', '925 hPa', ]
    
    eqpt_ = get_eqpt(fc_str, LEVELS[0], var)
    s = eqpt_.shape
    s = s[:1] + (len(LEVELS), ) + s[1:]
    eqpt = np.empty(s)
    eqpt[:,0,:,:] = eqpt_
    for pidx, level in zip(range(1,len(LEVELS)), LEVELS[1:]):
        eqpt[:,pidx,:,:] = get_eqpt(fc_str, level, var)

    dynfor.config.nsmooth = 10
    dynfor.config.tfp_mingrad_largescale = 3.75e-5
    dynfor.config.tfp_mingrad_smallscale = 5.25e-5
    dynfor.config.minsize = 75000.0e6

    frovo = dynlib.detect.frontalvolume_smallscale(eqpt, static.dx, static.dy)
    frovo = frovo[:,1,:,:]
    frovo[frovo > 0.5] = 1.0

    return frovo


def get_frontogenesis(fc_str, level, var):
    plev = level2plev(level)
    u = get_single(fc_str, plev, 'u')[:,np.newaxis,:,:]
    v = get_single(fc_str, plev, 'v')[:,np.newaxis,:,:]
    eqpt = get_eqpt(fc_str, level, var)
    eqpt = dynlib.utils.smooth_xy(eqpt, 3)[:,np.newaxis,:,:]

    w = np.zeros(u.shape)
    heat = np.zeros(u.shape)
    dz = np.ones(u.shape)

    frdiv, frdef, frtilt, frheat = dynlib.diag.frontogenesis_contributors(u, v, w, eqpt, heat, static.dx, static.dy, dz)

    return (frdef + frdiv).squeeze() * 1.0e5 # Convert to K/(100 km)/s


def get_T84_ff(fc_str, level, var):
    if (level, 'u_smooth') in CACHE:
        return np.sqrt(CACHE[level,'u_smooth']**2 + CACHE[level,'v_smooth']**2)

    plev = level2plev(level)
    u = get_single(fc_str, plev, 'u')
    v = get_single(fc_str, plev, 'v')

    # Filtering to T84 resolution
    u, conv = dynlib.utils.fill_nan(u)
    v, conv = dynlib.utils.fill_nan(v)
    br, bi, cr, ci = dynlib.sphere.sh_analysis_vector(u, v)
    dynlib.sphere.trunc_triangular(br, bi, 84)
    dynlib.sphere.trunc_triangular(cr, ci, 84)
    u, v = dynlib.sphere.sh_synthesis_vector(u.shape[2], br,bi,cr,ci)

    CACHE[level,'u_smooth'] = u
    CACHE[level,'v_smooth'] = v

    return np.sqrt(u**2 + v**2)

# Helpers for get_jetaxis
def _interpolate_location(dat, lat, lon, grid):
    ''' Interpolate dat to the jet locations (using the coordinates of its points) '''

    dati = np.empty(lat.shape[:2])
    for tidx in range(dat.shape[0]):
        func = interp.RectBivariateSpline(grid.y[::-1,0], grid.x[0,:], dat[tidx,::-1,:], kx=1, ky=1)
        dati[tidx,:] = func(lat[tidx,:], lon[tidx,:], grid=False)

    return dati

# For ERAi and ERA5 and global forecasts
def _idx2latlon(jetaxis):
    lon = (jetaxis[:,:,0]-1) * 0.5 - 180
    lat = 90.0 - (jetaxis[:,:,1]-1) * 0.5

    return lat, lon

def get_jetaxis(fc_str, level, var):
    dynfor.config.nsmooth = 0
    dynfor.config.minlen = 2.0e6
    dynfor.config.jetint_thres = 0.55e-8
    dynfor.config.searchrad = 1.5
    
    if not (level,'u_smooth') in CACHE:
        get_T84_ff(fc_str, level, var)
    
    # Jet axis detections
    ja, jaoff = dynlib.detect.jetaxis(10000, 10000, CACHE[level,'u_smooth'], CACHE[level,'v_smooth'], static.dx, static.dy)
    jaoff = jaoff.astype('i4')

    # Interpolate potential temperature to jet positions
    plev = level2plev(level)
    pt = get_single(fc_str, plev, 'pt')
    lat, lon = _idx2latlon(ja)
    pti = _interpolate_location(pt, lat, lon, static)
    ja = np.concatenate((ja, pti[:,:,np.newaxis]), axis=2)

    return ja, jaoff


def get_irot_wind(fc_str, level, var):
    plev = level2plev(level)
    u = get_single(fc_str, plev, 'u')
    v = get_single(fc_str, plev, 'v')

    uir, vir = dynlib.sphere.irot_wind(u, v)

    # Mask areas with ff_irot < 3.0 m/s
    ffir = np.sqrt(uir**2 + vir**2)
    uir[ffir < 3.0] = np.nan
    vir[ffir < 3.0] = np.nan

    return uir, vir


def get_cycfreq(fc_str, level, var):
    mslens = get_single_ens(fc_str, 'sfc', 'msl')
    mslctrl = get_single_ensctrl(fc_str, 'sfc', 'msl')

    dynfor.config.cyc_minsize = 0.5e6       # in km^2
    dynfor.config.cyc_maxsize = 4.5e6       # in km^2
    dynfor.config.cyc_maxoro = 1500         # in m
    dynfor.config.cyc_mindist = 750         # in km
    dynfor.config.cyc_minprominence = 200   # in Pa
    
    s = mslens.shape
    cycfreq = np.empty(s[0:1]+s[2:])
    indat = np.empty((s[1]+1,)+s[2:])
    for tidx in range(s[0]):
        print(f'{tidx}/{s[0]}')
        indat[0,:,:] = mslctrl[tidx,:,:]
        indat[1:,:,:] = mslens[tidx,:,:,:]
        cycmask, meta = dynlib.detect.cyclone_by_contour(indat, static)
        cycmask[cycmask > 0.5] = 1
        cycfreq[tidx,:,:] = cycmask.mean(axis=0)

    return cycfreq


def get_jetfreq(fc_str, level, var):
    plev = level2plev(level)
    uens = get_single_ens(fc_str, plev, 'u')
    uctrl = get_single_ensctrl(fc_str, plev, 'u')
    vens = get_single_ens(fc_str, plev, 'v')
    vctrl = get_single_ensctrl(fc_str, plev, 'v')

    f, staticl = metopen(f'{fc_str}/ec.ensctrl.{fc_str}.pv2000.u')
    f.close()

    dynfor.config.nsmooth = 0
    dynfor.config.minlen = 2.0e6
    dynfor.config.jetint_thres = 0.55e-8
    dynfor.config.searchrad = 1.5
    
    # Precalculate distances between points on a lat/lon grid
    green = dynlib.utils.dist_green_latlon(static.x[0,:], static.y[:,0])

    jetfreq = np.empty(uens.shape[0:1] + static.x.shape)
    for tidx in range(uens.shape[0]):
        uin = np.concatenate((uens[tidx,:,:,:], uctrl[tidx:tidx+1,:,:]), axis=0)
        vin = np.concatenate((vens[tidx,:,:,:], vctrl[tidx:tidx+1,:,:]), axis=0)

        # Jet axis detections
        ja, jaoff = dynlib.detect.jetaxis(10000, 100, uin, vin, staticl.dx, staticl.dy)
        jaoff = jaoff.astype('i4')
        ja[:,:,:2] = (ja[:,:,:2] -1)*3 +1 # Convert Fortran grid point indices from 1.5 to 0.5 deg grid
        jamask = dynlib.utils.mask_lines(static.x.shape[1], static.x.shape[0], ja, jaoff)
        
        # Find everything within 300 km of a jet axis and save
        mindists = dynlib.utils.dist_from_mask_latlon(jamask, green, static.x.shape[1]//2)
        jetfreq[tidx,:,:] = (mindists < 300.0e3).mean(axis=0)
    
    return jetfreq


def get_ensctrl_factory(level, var):
    def get_ensctrl(fc_str, level_, var_):
        return get_single_ensctrl(fc_str, level, var)

    return get_ensctrl


def get_ensmean_factory(level, var):
    def get_ensmean(fc_str, level_, var_):
        ens = get_single_ens(fc_str, level, var)
        ctrl = get_single_ensctrl(fc_str, level, var)

        return (ens.sum(axis=1) + ctrl)/(ens.shape[1]+1)

    return get_ensmean


get_special = {
    'Equivalent potential temperature': get_eqpt,
    'Wind speed': get_ff,
    '10m Wind speed': get_ff10,
    '2m Relative humidity': get_rh2m,
    'Cold-air outbreak index': get_cao,
    'Convective precipitation': get_cp,
    'Large-scale precipitation': get_lsp,
    'Total precipitation': get_tp,
    'Surface sensible heat flux': get_sshf,
    'Surface latent heat flux': get_slhf,
    'Surface total heat flux': get_sthf,
    'Sea-surface temperature': get_sst,
    'Sea ice concentration': get_siconc,
    'Column integral water vapour transport': get_absiwvt,
    'Water vapour transport axes': get_iwvt_axis,
    'Water vapour anomalous transport axes': get_iwvta_axis,
    'Temperature anomaly': get_t_ano,
    'Temperature percentiles': get_t_perc,
    'Frontal volumes': get_frovo,
    'Frontogenesis': get_frontogenesis,
    'Jet axes': get_jetaxis,
    'Wind speed filtered to T84': get_T84_ff,
    'Irrot. wind barbs': get_irot_wind,
    'Cyclone occurrence': get_cycfreq,
    'Jet occurrence within 300 km': get_jetfreq,
    'Ensemble mean sea level pressure': get_ensmean_factory(level='sfc', var='msl'),
    'Ensemble ctrl sea level pressure': get_ensctrl_factory(level='sfc', var='msl'),
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
        'plev': ['z500_msl', 't850_msl', 'eqpt850_cape', 'tcwv', 'iwvt_axis', 't850_perc', ],
        'isentropic': ['pvpt315_irot_wind', 'pvpt330_irot_wind', ],
        'pv2': ['ptpv2_jets', ],
        'ens': ['cycfreq_msl', 'jetfreq_msl', ],
        'test': [],
        'sfc': ['tcc', 'ff10_gusts', 'cao_winds', 'sshf_winds', 'slhf_winds', 'rh2m_tp', ],
    }
    
    if len(sys.argv) > 1:
        for arg in sys.argv[1:]:
            if arg in PLOT_SETS:
                plots = [plotter(domainname, domains[domainname], 'ec', plotname, plot)
                    for domainname, plots_by_domain in plots['ec'].items() for plotname, plot in plots_by_domain.items()
                    if plotname in PLOT_SETS[arg]
                ]
                print('Plotting plot set "%s".' % arg)
            else:
                raise ValueError('Unknown plot set "%s".' % arg)
    else:
        plots = [plotter(domainname, domains[domainname], 'ec', plotname, plot)
            for domainname, plots_by_domain in plots['ec'].items() for plotname, plot in plots_by_domain.items()]

        print('No plot set specified, plotting all plot sets.')

    print(len(plots))
    
    fc_str = forecast.strftime('%Y%m%d%H')
    conf.datapath.insert(1, '/share/base/ecmwf')
    
    # Load surface pressure to be able to mask areas under ground
    plev, q = 'sfc', 'msl'
    fname = f'{fc_str}/ec.for.{fc_str}.{plev}.{q}'
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
    leadlist = list(range(0,72,3))
    leadlist.extend(range(72,241,6))
    leadlist_link = range(0,241,12)

    render_webpage('natl', 'ec', forecast, fclist, leadlist, leadlist_link)
    render_webpage('npolar', 'ec', forecast, fclist, leadlist, leadlist_link)
    render_webpage('spolar', 'ec', forecast, fclist, leadlist, leadlist_link)
    render_webpage('lehmkuhl', 'ec', forecast, fclist, leadlist, leadlist_link)
    render_webpage('tindpac', 'ec', forecast, fclist, leadlist, leadlist_link)

# the end
