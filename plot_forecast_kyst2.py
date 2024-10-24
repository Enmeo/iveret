#!/usr/bin/env python
# -*- encoding: utf-8

import copy

import matplotlib as mpl
mpl.use('Agg')

from numpy import ma
import pyproj

from plotconfig_ihavet import *
from settings.common2 import *

import dynlib.diag
import dynlib.detect
import dynlib.thermodyn
import dynlib.utils

from current_fc_kyst import get_current_fc_kyst



q_map = {
    'Sea-surface salinity': 'salinity',
}


def get_single(fc_str, plev, q):
    fname1 = f'norkyst_an_{fc_str}.{plev}'
    fname2 = f'norkyst_fc_{fc_str}.{plev}'
    #try:
    f, dat1 = metopen(fname1, q, no_static=True)
    f, dat2 = metopen(fname2, q, no_static=True)
    dat = np.concatenate((dat1, dat2), axis=0)
    dat = dat.squeeze()
    #except:
    #    dat = None

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


# Copy of rotate_vector function from Basemap 1.1.0, here used for the inverse rotation required to plot NorKyst flow vectors
def rotate_vector_i(proj,uin,vin,lons,lats,returnxy=False):
    """
    Rotate a vector field (``uin,vin``) on a rectilinear grid
    with longitudes = ``lons`` and latitudes = ``lats`` from
    map projection (x/y) into geographical (lat/lon) coordinates.

    Differs from transform_vector in that no interpolation is done.
    The vector is returned on the same grid, but rotated into
    x,y coordinates.

    The input vector field is defined in spherical coordinates (it
    has eastward and northward components) while the output
    vector field is rotated to map projection coordinates (relative
    to x and y). The magnitude of the vector is preserved.

    .. tabularcolumns:: |l|L|

    ==============   ====================================================
    Arguments    Description
    ==============   ====================================================
    uin, vin     input vector field on a lat/lon grid.
    lons, lats       Arrays containing longitudes and latitudes
             (in degrees) of input data in increasing order.
             For non-cylindrical projections (those other than
             ``cyl``, ``merc``, ``cyl``, ``gall`` and ``mill``) lons
             must fit within range -180 to 180.
    ==============   ====================================================

    Returns ``uout, vout`` (rotated vector field).
    If the optional keyword argument
    ``returnxy`` is True (default is False),
    returns ``uout,vout,x,y`` (where ``x,y`` are the map projection
    coordinates of the grid defined by ``lons,lats``).
    """
    # if lons,lats are 1d and uin,vin are 2d, and
    # lats describes 1st dim of uin,vin, and
    # lons describes 2nd dim of uin,vin, make lons,lats 2d
    # with meshgrid.
    if lons.ndim == lats.ndim == 1 and uin.ndim == vin.ndim == 2 and\
       uin.shape[1] == vin.shape[1] == lons.shape[0] and\
       uin.shape[0] == vin.shape[0] == lats.shape[0]:
        lons, lats = np.meshgrid(lons, lats)
    else:
        if not lons.shape == lats.shape == uin.shape == vin.shape:
            raise TypeError("shapes of lons,lats and uin,vin don't match")
    x, y = proj(lons, lats)
    # rotate from geographic to map coordinates.
    if ma.isMaskedArray(uin):
        mask = ma.getmaskarray(uin)
        masked = True
        uin = uin.filled(1)
        vin = vin.filled(1)
    else:
        masked = False

    # Map the (lon, lat) vector in the complex plane.
    uvc = uin + 1j*vin
    uvmag = np.abs(uvc)
    theta = np.angle(uvc)

    # Define a displacement (dx, dy) that moves all
    # positions (x, y) a small distance in the
    # direction of the original vector.
    dc = 1.0 * np.exp(theta*1j)
    dy = dc.imag 
    dx = dc.real

    # Add displacement to original location and find the native coordinates.
    x1 = x + dx
    y1 = y + dy
    lon1, lat1 = proj(x1, y1, inverse=True)

    # Determine the angle of the displacement in the native coordinates.
    vecangle = np.arctan2(lat1-lats, lon1-lons)

    # Compute the x-y components of the original vector.
    uvcout = uvmag * np.exp(1j*vecangle)
    uout = uvcout.real
    vout = uvcout.imag

    if masked:
        uout = ma.array(uout, mask=mask)
        vout = ma.array(vout, mask=mask)
    if returnxy:
        return uout,vout,x,y
    else:
        return uout,vout


def get_temperature(fc_str, level, var):
    plev = level2plev(level)
    t = get_single(fc_str, plev, 'temperature')

    return t + 273.16 # is expected to be returned in SI units rather than deg Celius

def get_uv(fc_str, level, var):
    plev = level2plev(level)
    u_ = get_single(fc_str, plev, 'u')
    v_ = get_single(fc_str, plev, 'v')

    proj = pyproj.Proj("+proj=stere +lat_0=90 +lon_0=70 +lat_ts=60 +units=m +a=6.371e+06 +e=0 +no_defs")
    
    u = np.empty(u_.shape)
    v = np.empty(v_.shape)
    for tidx in range(u.shape[0]):
        u[tidx,:,:], v[tidx,:,:] = rotate_vector_i(proj, u_[tidx,:,:], v_[tidx,:,:], static.x, static.y)

    return u, v

def get_bathymetry(fc_str, level, var):
    t = get_single(fc_str, 'sfc', 'temperature')
    f, bathy_ = metopen('settings/norkyst_bathymetry', 'h', no_static=True)

    bathy = np.empty((t.shape[0], *bathy_.shape))
    bathy[:,:,:] = bathy_[np.newaxis,:,:]

    return bathy


def get_ff(fc_str, level, var):
    plev = level2plev(level)
    u = get_single(fc_str, plev, 'u')
    v = get_single(fc_str, plev, 'v')

    return np.sqrt(u**2 + v**2)

get_special = {
    'Sea-surface temperature': get_temperature,
    'Surface current speed': get_ff,
    'Surface currents': get_uv,
    'Bathymetry': get_bathymetry,
}


# -----------------------------------------------------------------------------

if __name__ == '__main__':
    # Most recent available data
    forecast = get_current_fc_kyst()
    
    # Override
    #forecast = dt(2019,8,27,18)
    plot_only_init = False
    
    print('Plotting the NorKyst %s forecasts' % forecast.strftime('%Y-%m-%d %H'))
    
    plots = [plotter(domainname, domains[domainname], 'no_kyst', plotname, plot)
            for domainname, plots_by_domain in plots['no_kyst'].items() for plotname, plot in plots_by_domain.items()]
    #plots = [plotter(domainname, domains[domainname], 'no_kyst', plotname, plot)
    #        for domainname, plots_by_domain in plots['no_kyst'].items() for plotname, plot in plots_by_domain.items()
    #        if plotname == 'sst_sfccur']
    
    fc_str = forecast.strftime('%Y%m%d%H')
    conf.datapath.insert(1, '/share/base/metno_kyst')
    
    # Load surface pressure to be able to mask areas under ground
    fname1 = f'norkyst_an_{fc_str}.sfc'
    fname2 = f'norkyst_fc_{fc_str}.sfc'
    f1, static = metopen(fname1)
    f2, static2 = metopen(fname2)

    # We need to replace the auto-detected x dimension with the alternative lon dimension
    static.x = f1.variables['lon'][::]
    static.y = f2.variables['lat'][::]
    static.gridtype = 'latlon'
    static.t_parsed = np.concatenate((static.t_parsed, static2.t_parsed), axis=0)

    f1.close()
    f2.close()
        
    data = {}
    for plot in plots:
        for plev, q in plot.requires:
            if (plev,q) in data:
                continue

            if q in get_special:
                data[plev,q] = get_special[q](fc_str, plev, q)
            else:
                data[plev,q] = get(fc_str, plev, q)
    
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

    fclist = [forecast - td(i) for i in range(5)]
    leadlist = range(0,67,3)
    leadlist_link = range(0,67,6)
    render_webpage('bergen', 'no_kyst', forecast, fclist, leadlist, leadlist_link)
    render_webpage('vestland', 'no_kyst', forecast, fclist, leadlist, leadlist_link)
    render_webpage('snorway', 'no_kyst', forecast, fclist, leadlist, leadlist_link)

# the end
