#!/usr/bin/env python
# -*- encoding: utf-8


import matplotlib as mpl
mpl.use('Agg')

import copy
from mpl_toolkits.basemap import pyproj
from numpy import ma

from dynlib.shorthands import *
from settings.metno import *

import dynlib.utils

from current_fc_kyst import get_current_fc_kyst

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

######################################################
# The base of _everything_

# Genering plot
class plotter(object):
    filetype = 'png'
    fcname = 'no_kyst'
    
    # Add colorbar and legend
    decorations = False

    # Which data is required for the plot
    requires=[]
    requires_diagnostic = []
    fmt = '%Y%m%d%H'

    std_plotconf = {
        'm': proj.S_Norway,
        'coastcolor': None,
        'coastwidth': 0.5,
        'grid_alpha': 0.25,
        'grid_linestyle': '-',
        'grid_latmax': 90,
        'show': False,
        'title': None,
    }
    
    figsize = (6.4,6.4)
    figsize_deco = (7.27273,6.4)
    
    # Do the art; to be overriden in derived classes
    def plot(self, data, static, dateinit, datevalid):
        self.std_plotconf['save'] = '%s_%s_from_%s_for_%s.%s' % (
                self.fcname, self.plotname, 
                dateinit.strftime(self.fmt), datevalid.strftime(self.fmt), 
                self.filetype
        )

        if self.decorations:
            fi = plt.figure(figsize=self.figsize_deco, dpi=96)
            self.std_plotconf['show_legend'] = True
            self.std_plotconf['cb_orientation'] = 'vertical'
            self.std_plotconf['cb_expand_fig_fraction'] = 0.12
            self.std_plotconf['cb_shrink'] = 0.65
            
        else:
            fi = plt.figure(figsize=self.figsize, dpi=96)
            self.std_plotconf['cb_disable'] = True

        fi.subplotpars.update(left=0.001, right=0.999, top=0.999, bottom=0.001)
        
        data_available = True
        for qplev in self.requires:
            data_available &= qplev in data

        if not data_available:
            fi.text(0.5, 0.5, 'Error: Data unavailable', horizontalalignment='center', fontsize=24, bbox=dict(facecolor='red', alpha=0.5))
            plt.savefig(plotpath + '/' + self.std_plotconf['save'])
            return True

        else:
            return False


class Vestland(plotter):
    fcname = plotter.fcname + '_vestland'

    std_plotconf = copy.copy(plotter.std_plotconf)
    std_plotconf['m'] = proj.Vestland

    figsize = (6.4,6.4)
    figsize_deco = (7.27273,6.4)

    
class Bergen(plotter):
    fcname = plotter.fcname + '_bergen'

    std_plotconf = copy.copy(plotter.std_plotconf)
    std_plotconf['m'] = proj.Bergen

    figsize = (6.4,6.4)
    figsize_deco = (7.27273,6.4)
    

######################################################
# SST and surface currents
class sst_sfccur(plotter):
    requires = ['temperature', 'u', 'v']
    plotname = 'sst_sfccur'

    overlay_conf = {'vector_space_interval': 15}

    def plot(self, data, static, dateinit, datevalid):
        done = plotter.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        proj = pyproj.Proj("+proj=stere +lat_0=90 +lon_0=70 +lat_ts=60 +units=m +a=6.371e+06 +e=0 +no_defs")
        u, v = rotate_vector_i(proj, data['u'], data['v'], static.x, static.y)

        overlays = [
            fig.map_overlay_contour(static.bathymetry, static, 
                scale=[500,1000,1500],
                colors='0.2',
                linewidths=1,
                alpha=0.7,
            ),
            fig.map_overlay_quiver(u, v, static, 
                vector_disable_interpolation=True,
                quiver_width=0.0015,
                quiver_length=30.0,
                **self.overlay_conf
            ),
        ]
        plotconf = pconf.merge('sfc', 'sst',
                overlays=overlays,
                scale=np.arange(0,21.1,0.5),
                ticks=range(0,21,5),
                hook=None,
                **self.std_plotconf
        )
        fig.map(data['temperature'], static, **plotconf)

        return True


class sst_sfccur_Vestland(sst_sfccur,Vestland):
    requires = ['temperature', 'u', 'v']
    plotname = 'sst_sfccur'

    overlay_conf = {'vector_space_interval': 5}


class sst_sfccur_Bergen(sst_sfccur,Bergen):
    requires = ['temperature', 'u', 'v']
    plotname = 'sst_sfccur'

    overlay_conf = {'vector_space_interval': 1}


######################################################
# Surface current speed and direction
class ff_sfccur(plotter):
    requires = ['u', 'v']
    plotname = 'ff_sfccur'

    overlay_conf = {'vector_space_interval': 15}

    def plot(self, data, static, dateinit, datevalid):
        done = plotter.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        proj = pyproj.Proj("+proj=stere +lat_0=90 +lon_0=70 +lat_ts=60 +units=m +a=6.371e+06 +e=0 +no_defs")
        u, v = rotate_vector_i(proj, data['u'], data['v'], static.x, static.y)
        ff = np.sqrt(data['u']**2 + data['v']**2)

        overlays = [
            fig.map_overlay_contour(static.bathymetry, static, 
                scale=[500,1000,1500],
                colors='0.9',
                linewidths=1,
                alpha=0.7,
            ),
            fig.map_overlay_quiver(u, v, static, 
                vector_disable_interpolation=True,
                quiver_width=0.0015,
                quiver_length=30.0,
                **self.overlay_conf
            ),
        ]
        plotconf = pconf.merge('sfc', 'ff10',
                overlays=overlays,
                cmap=cm.RdYlCyBu2,
                hook=lambda x: x*100, # from m/s to cm/s
                scale=np.arange(0,201,10),
                ticks=range(0,201,40),
                **self.std_plotconf
        )
        fig.map(ff, static, **plotconf)

        return True


class ff_sfccur_Vestland(ff_sfccur,Vestland):
    requires = ['u', 'v']
    plotname = 'ff_sfccur'

    overlay_conf = {'vector_space_interval': 5}


class ff_sfccur_Bergen(ff_sfccur,Bergen):
    requires = ['u', 'v']
    plotname = 'ff_sfccur'

    overlay_conf = {'vector_space_interval': 1}


######################################################
# Surface salinity and currents
class sss_sfccur(plotter):
    requires = ['salinity', 'u', 'v']
    plotname = 'sss_sfccur'

    overlay_conf = {'vector_space_interval': 15}

    def plot(self, data, static, dateinit, datevalid):
        done = plotter.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        proj = pyproj.Proj("+proj=stere +lat_0=90 +lon_0=70 +lat_ts=60 +units=m +a=6.371e+06 +e=0 +no_defs")
        u, v = rotate_vector_i(proj, data['u'], data['v'], static.x, static.y)
        ff = np.sqrt(data['u']**2 + data['v']**2)

        overlays = [
            fig.map_overlay_contour(static.bathymetry, static, 
                scale=[500,1000,1500],
                colors='0.9',
                linewidths=1,
                alpha=0.7,
            ),
        fig.map_overlay_quiver(u, v, static, 
                vector_disable_interpolation=True,
                quiver_width=0.0015,
                quiver_length=30.0,
                **self.overlay_conf
            ),
        ]
        sss_scale = [0, 20, 30, 32, 32.5, 33, 33.3, 33.6, 33.8, 34, 34.2, 34.4, 34.6, 34.8, 35, 35.2, 37]
        plotconf = pconf.merge('sfc', 'sst',
                overlays=overlays,
                cmap='viridis_r', # Set a colormap
                scale=sss_scale,
                norm=mpl.colors.BoundaryNorm(sss_scale, 256),
                ticks=sss_scale,
                cb_tickspacing='uniform',
                extend='neither',
                hook=None,
                **self.std_plotconf
        )
        fig.map(data['salinity'], static, **plotconf)

        return True


class sss_sfccur_Vestland(sss_sfccur,Vestland):
    requires = ['u', 'v']
    plotname = 'sss_sfccur'

    overlay_conf = {'vector_space_interval': 5}


class sss_sfccur_Bergen(sss_sfccur,Bergen):
    requires = ['u', 'v']
    plotname = 'sss_sfccur'

    overlay_conf = {'vector_space_interval': 1}


# -----------------------------------------------------------------------------

if __name__ == '__main__':
    # Most recent available data
    forecast = get_current_fc_kyst()
    plot_only_init = False
    
    print('Plotting the NorKyst %s forecasts' % forecast.strftime('%Y-%m-%d %H'))
    
    plots = [
        sst_sfccur(), sst_sfccur_Vestland(), sst_sfccur_Bergen(),
        ff_sfccur(),  ff_sfccur_Vestland(),  ff_sfccur_Bergen(),
        sss_sfccur(), sss_sfccur_Vestland(), sss_sfccur_Bergen(),
    ]
    
    fname1 = 'norkyst_an_%s.sfc' % forecast.strftime('%Y%m%d%H')
    fname2 = 'norkyst_fc_%s.sfc' % forecast.strftime('%Y%m%d%H')
    try:
        #print('Looking for %s' % fname)
        f1, static = metopen(fname1)
        f2, static_ = metopen(fname2)
    
        # We need to replace the auto-detected x dimension with the alternative lon dimension
        static.x = f1.variables['lon'][::]
        static.y = f1.variables['lat'][::]
        static.gridtype = 'latlon'
        static.t_parsed = np.concatenate((static.t_parsed, static_.t_parsed), axis=0)
        #static.rebuild_grid()
    except ValueError:
        print('Warning: File %s or %s not readable.' % (fname1, fname2))
        class Bunch(dict):
            def __init__(self,**kw):
                dict.__init__(self,kw)
                self.__dict__ = self
        f1 = Bunch(variables=[], close=lambda: None)
        f2 = Bunch(variables=[], close=lambda: None)
        
        t = range(0,67,3)
        static = Bunch(t=t, t_parsed=[forecast + i*td(0,3600) for i in t])
    
    data = {}
    for plot in plots:
        plot.error = False
        for q in plot.requires:
            if q not in f1.variables or q not in f2.variables:
                print('%s not available!' % q)
                plot.error = True
            elif q not in data:
                data[q] = np.concatenate((
                    dynlib.utils.scale(f1.variables[q]).squeeze(),
                    dynlib.utils.scale(f2.variables[q]).squeeze(),
                ), axis=0)
        
        if not plot.error:
            for fun in plot.requires_diagnostic:
                fun(plot, data, static)
    
    f1.close()
    f2.close()
    
    conf.datapath.insert(1, basepath) # for the bathymetry
    f, bathy = metopen('settings/norkyst_bathymetry', 'h', no_static=True)
    static.bathymetry = bathy
    
    for tidx, date in zip(range(len(static.t_parsed)), static.t_parsed):
        # Plot only 3-hourly data to speed up plotting
        if not date.hour % 3 == 0:
            continue
    
        # Plot only initial time step
        if plot_only_init and not date == forecast:
            continue
        
        print(tidx, date)
        data_inst = {}
        for q in data:
            data_inst[q] = data[q][tidx]
        
        for plot in plots:
            plot.plot(data_inst, static, forecast, date)
            plt.close()


# the end
