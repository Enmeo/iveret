#!/usr/bin/env python
# -*- encoding: utf-8

import matplotlib as mpl
mpl.use('Agg')
from mpl_toolkits.basemap import Basemap

import copy
import sys
import pygrib

import dynlib
import dynlib.detect
import dynlib.diag
import dynlib.sphere
import dynlib.thermodyn
import dynlib.utils

from dynlib.shorthands import *
from dynlib.gridlib import grid_by_latlon
from settings.gfs import *
from current_fc_gfs import *


######################################################
# The base of _everything_

# Genering plot
class plotter(object):
    filetype = 'png'
    fcname = 'noaa_for'
    
    # Add colorbar and legend
    decorations = False

    # Which data is required for the plot
    requires=[]
    requires_diagnostic = []
    fmt = '%Y%m%d%H'

    std_plotconf = {
        'm': proj.NAfcmap,
        'coastcolor': 'k',
        'coastwidth': 0.5,
        'grid_alpha': 0.25,
        'grid_linestyle': '-',
        'grid_latmax': 90,
        'show': False,
        'title': None,
    }

    figsize = (7.2,4.8)
    figsize_deco = (8.18182,4.8)
    
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
            plt.savefig(conf.plotpath + '/' + self.std_plotconf['save'])
            return True

        else:
            return False


# Base for all northern stereographic maps
class npolar(plotter):
    fcname = plotter.fcname + '_npolar'

    std_plotconf = copy.copy(plotter.std_plotconf)
    std_plotconf['m'] = lambda: Basemap(projection='npstere',boundinglat=10,lon_0=-50,resolution='c', area_thresh=10000)

    figsize = (6.4,6.4)
    figsize_deco = (7.27273,6.4)


# Base for all southern stereographic maps
class spolar(plotter):
    fcname = plotter.fcname + '_spolar'

    std_plotconf = copy.copy(plotter.std_plotconf)
    std_plotconf['m'] = proj.s_hemisphere

    figsize = (6.4,6.4)
    figsize_deco = (7.27273,6.4)



######################################################
# Plot archetypes

# Temperature shading and MSLP contours
class t_msl(plotter):
    pass

# Geopotential shading and MSLP contours
class z_msl(plotter):
    pass

# Anything requiring specific humidity
class precip(plotter):
    # From relative to specific humidity
    def cal_trr(self, data, plev, static):
        if not ('trr', plev) in data:
            data['trr',plev] = data['lsrr',plev] + data['crr',plev]

# Anything requiring specific humidity
class spec_hum(plotter):
    # From relative to specific humidity
    def cal_spec_hum(self, data, plev, static):
        if not ('q', plev) in data:
            e = dynlib.thermodyn.e_from_rh(data['rh',plev], data['t',plev])
            p = np.ones(e.shape) * 100 * int(plev)
            data['q',plev] = dynlib.thermodyn.q_from_e(e, p)

# Anything requiring potential temperature
class theta(plotter):
    # From relative to specific humidity
    def cal_theta(self, data, plev, static):
        if not ('pt', plev) in data:
            data['pt',plev] = dynlib.thermodyn.theta_from_temp(data['t',plev], data['p',plev])

# Integrated water vapour constant, based on a given set of pressure levels
class iwvtrans(spec_hum):
    pbot = 1000
    ptop = 200
    
    # plevs must be in decending order
    def cal_iwvtransport(self, data, plevs, static):
        for plev in plevs:
            self.cal_spec_hum(data, plev, static)

        if not ('iwvtransx', 'sfc') in data:
            data['iwvtransx','sfc'] = np.zeros(data['q',plevs[0]].shape)
            data['iwvtransy','sfc'] = np.zeros(data['q',plevs[0]].shape)

            for k, plev in zip(range(len(plevs)), plevs):
                if k == 0:
                    p0 = self.pbot
                else:
                    p0 = (float(plevs[k-1])+float(plev))/2
                if k == len(plevs)-1:
                    p1 = self.ptop
                else:
                    p1 = (float(plev)+float(plevs[k+1]))/2

                data['iwvtransx','sfc'] += (p0-p1)*data['u',plev]*data['q',plev]
                data['iwvtransy','sfc'] += (p0-p1)*data['v',plev]*data['q',plev]

            data['iwvtransx','sfc'] /= self.pbot-self.ptop
            data['iwvtransy','sfc'] /= self.pbot-self.ptop

# Deformation
class deform(plotter):
    def cal_deform(self, data, plev, static):
        if not ('defabs', plev) in data:
            data['defabs',plev] = dynlib.diag.def_total(data['u',plev], data['v', plev], static.dx, static.dy)
        if not ('defang', plev) in data:
            data['defang',plev] = dynlib.diag.def_angle(data['u',plev], data['v', plev], static.dx, static.dy)

# Frontal diagnostics
class fronts(plotter):
    def detect_frontalvolumes(self, data, plev, static):
        dynfor.config.nsmooth = 10
        dynfor.config.tfp_mingrad_largescale = 3.75e-5
        dynfor.config.tfp_mingrad_smallscale = 5.25e-5
        dynfor.config.minsize = 75000.0e6

        if not ('frovo', plev) in data:
            PLEVS = ['700', '850', '925', ]
            pidx = PLEVS.index(plev)

            s = data['t',plev].shape
            s = s[:1] + (len(PLEVS), ) + s[1:]
            eqpt = np.empty(s)
            
            p = np.empty(data['t',plev].shape)
            for pidx,plev_ in zip(range(len(PLEVS)), PLEVS):
                if not ('eqpt', plev_) in data:
                    p[:,:,:] = 100.0 * int(plev_)
                    data['eqpt',plev_] = dynlib.thermodyn.thetae_from_q(data['q',plev_], data['t',plev_], p)

                eqpt[:,pidx,:,:] = data['eqpt',plev_]        

            frovo = dynlib.detect.frontalvolume_smallscale(eqpt, static.dx, static.dy)
            del eqpt
            
            data['frovo',plev] = frovo[:,pidx,:,:]
            data['frovo',plev][data['frovo',plev] > 0.5] = 1
            del frovo


    def detect_frontlines(self, data, plev, static):
        dynfor.config.nsmooth = 30
        dynfor.config.frint_thres = 2.5e-5

        if not ('fronts', plev) in data:
            if not ('eqpt', plev) in data:
                p = np.ones(data['t',plev].shape) * 100.0 * int(plev)
                data['eqpt',plev] = dynlib.thermodyn.thetae_from_q(data['q',plev], data['t',plev], p)

            data['fronts',plev], data['froff',plev] = dynlib.detect.frontline_at_maxgrad(10000,1000, 
                    data['eqpt',plev], data['u',plev], data['v',plev], static.dx, static.dy)
            data['froff',plev] = data['froff',plev].astype('i4')

# Wind speed
class ff(plotter):
    def cal_ff(self, data, plev, static):
        if not ('ff', plev) in data:
            data['ff',plev] = np.sqrt(data['u',plev]**2.0 + data['v',plev]**2.0)

# 10m wind speed
class ff10(ff):
    def cal_ff10(self, data, plev, static):
        if not ('ff10', plev) in data:
            data['ff10',plev] = np.sqrt(data['u10',plev]**2.0 + data['v10',plev]**2.0)


# Potential vorticity and divergent wind
class irot_wind(plotter):
    def cal_irot_wind(self, data, plev, static):
        if not ('u_irot', plev) in data:
            data['u_irot',plev], data['v_irot',plev] = dynlib.sphere.irot_wind(data['u',plev], data['v',plev])

            # Mask areas with ff_irot < 2.0 m/s
            ff_irot = np.sqrt(data['u_irot',plev]**2.0 + data['v_irot',plev]**2.0)
            data['u_irot',plev][ff_irot < 3.0] = np.nan
            data['v_irot',plev][ff_irot < 3.0] = np.nan

# Jets / Jet axes
class jets(ff):
    def cal_jetaxis(self, data, plev, static):
        dynfor.config.nsmooth = 0
        dynfor.config.minlen = 2.0e6 
        dynfor.config.jetint_thres = 0.55e-8
        dynfor.config.searchrad = 1.5

        if not ('u_smooth',plev) in data:
            # Interpolation to T84 resolution
            umask = np.isnan(data['u',plev])
            vmask = np.isnan(data['v',plev])
            u, conv = dynlib.utils.fill_nan(data['u',plev])
            v, conv = dynlib.utils.fill_nan(data['v',plev])
            br, bi, cr, ci = dynlib.sphere.sh_analysis_vector(u, v)
            dynlib.sphere.trunc_triangular(br, bi, 84)
            dynlib.sphere.trunc_triangular(cr, ci, 84)
            data['u_smooth',plev], data['v_smooth',plev] = dynlib.sphere.sh_synthesis_vector(data['u',plev].shape[2], br,bi,cr,ci)
            data['ff_smooth',plev] = np.sqrt(data['u_smooth',plev]**2.0 + data['v_smooth',plev]**2.0)
        
        if not ('jetaxis', plev) in data:
            # Jet axis detections
            data['jetaxis',plev], data['jaoff',plev] = dynlib.detect.jetaxis(10000, 10000, 
                    data['u_smooth',plev], data['v_smooth',plev], static.dx, static.dy)
            data['jaoff',plev] = data['jaoff',plev].astype('i4')


# Percentile plots
class percentiles(plotter):
    BASE_PATH = '/home/ubuntu/data'

    def cal_percentiles(self, data, info, static):
        q, plev, base_period = info
        qp = '%s_percs' % q
        qa = '%s_ano' % q
        if not (qp, plev) in data or not (qa,plev) in data:
            filename = self.BASE_PATH + '/ei.ans.%s.%s.%s.npz' % (base_period, plev, qp)
            print('Using base data from %s' % filename)
            f = np.load(filename)
            base_data = f['dat']
            percs = f['percs']
            f.close()
            
            # Current month (index, starting with January as 0)
            mon = static.t_parsed[0].month - 1
            
            # Calculate anomalies compared to median
            idx = np.argwhere(percs == 0.5)[0,0] 
            data[qa,plev] = data[q,plev] - base_data[mon,idx]

            # Find percentiles
            data[qp,plev] = np.empty(data[q,plev].shape, dtype='i1') * np.nan
            mask = data[q,plev] < base_data[mon,0][np.newaxis,:,:]
            data[qp,plev][mask] = 0
            for i in range(1, base_data.shape[1]):
                dmin = base_data[mon,i-1][np.newaxis,:,:]
                dmax = base_data[mon,i][np.newaxis,:,:]
                mask = (data[q,plev] >= dmin) & (data[q,plev] < dmax)
                data[qp,plev][mask] = i
            i += 1
            mask = data[q,plev] >= base_data[mon,-1][np.newaxis,:,:]
            data[qp,plev][mask] = i


######################################################
# Specific plots

# Temperature@850hPa shading and MSLP contours
class t850_msl(t_msl):
    requires = [('t', '850'), ('u', '850'), ('v', '850'), ('msl', 'sfc'), ]
    plotname = 't850_msl'

    def plot(self, data, static, dateinit, datevalid):
        done = t_msl.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        overlays = [
            fig.map_overlay_contour(data['msl','sfc'], static, **conf.plot.merge('sfc', 'msl', 
                linewidths=[0.5], 
                scale=range(900,1070,5),
                alpha=0.8,) ), 
            fig.map_overlay_contour(data['t','850'], static, **conf.plot.merge('850', 't',
                linewidths=[1], 
                linestyles='dashed',
                scale=range(0,2,2) ) ),
            fig.map_overlay_barbs(data['u','850'], data['v','850'], static, **conf.plot.merge('sfc', 'ff10', 
                alpha=0.5,
                linewidths=0.5,
                length=5,
                **self.std_plotconf) ),
        ]
        plotconf = conf.plotf.merge('850', 't',
                overlays=overlays,
                scale=range(-34,36,2),
                ticks=range(-30,31,10),
                **self.std_plotconf
        )
        fig.map(data['t', '850'], static, **plotconf)

        return True


# Temperature@850hPa shading and MSLP contours
class t850_perc(t_msl, percentiles):
    requires = [('t', '850'), ]
    requires_diagnostic = [(percentiles.cal_percentiles, ['t', '850', '1979-2017', ]), ]
    plotname = 't850_perc'

    def plot(self, data, static, dateinit, datevalid):
        done = t_msl.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        s = [-30,-25,-21,-18,-15,-13,-11,-9,-7,-5,-3,-1,1,3,5,7,9,11,13,15,18,21,25,30]

        overlays = [
            fig.map_overlay_contour(data['t_percs', '850'], static, plev=None, q='perc', 
                colors='w', scale=[0.5, 18.5]),
            fig.map_overlay_contour(data['t_percs', '850'], static, plev=None, q='perc', 
                colors='0.3', scale=[1.5, 17.5]),
            fig.map_overlay_contour(data['t_percs', '850'], static, plev=None, q='perc', 
                scale=[3.5, 15.5]),
        ]
        plotconf = conf.plotf.merge('850', 't_ano',
                scale=s,
                norm=mpl.colors.BoundaryNorm([-np.inf,]+s+[np.inf,], 256),
                cb_tickspacing='uniform',
                overlays=overlays,
                **self.std_plotconf
        )
        fig.map(data['t_ano', '850'], static, **plotconf)

        return True


# Geopotential@5000hPa shading and MSLP contours
class z500_msl(z_msl):
    requires = [('z', '500'), ('msl', 'sfc')]
    plotname = 'z500_msl'

    def plot(self, data, static, dateinit, datevalid):
        done = z_msl.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        overlays = [
            fig.map_overlay_contour(data['msl','sfc'], static, **conf.plot.merge('sfc','msl',  
                alpha=0.8,
                contour_labels=True, 
                contour_labels_format='%g',
                linewidths=[1], 
                scale=range(900,1070,5) ) ),
            #fig.map_overlay_contour(data['z','500'], static, **conf.plot.merge('500', 'z',
            #    contour_labels=True, 
            #    colors='white',
            #    linewidths=[1],
            #    linestyles='dashed',
            #    scale=range(472,601,16) ) ),
            fig.map_overlay_contour(data['z','500'], static, **conf.plot.merge('500', 'z',
                contour_labels=False, 
                colors='white',
                linewidths=[2],
                scale=range(552,554,2) ) ), 
        ]
        plotconf = conf.plotf.merge('500', 'z',
                overlays=overlays,
                scale=range(476,604,4),
                ticks=range(480,601,20),
                **self.std_plotconf
        )
        fig.map(data['z','500'], static, **plotconf)

        return True


# Geopotential@500hPa shading and MSLP contours
class z500_msl_npolar(z500_msl,npolar):
    requires = [('z', '500'), ('msl', 'sfc')]
    plotname = 'z500_msl'


# Geopotential@500hPa shading and MSLP contours
class z500_msl_spolar(z500_msl,spolar):
    requires = [('z', '500'), ('msl', 'sfc')]
    plotname = 'z500_msl'


# Potential vorticity@300K shading and wind barbs
class pvpt315_wind(irot_wind):
    requires = [('pv', 'pt315'), ('u', 'pt315'), ('v', 'pt315')]
    requires_diagnostic = [(irot_wind.cal_irot_wind, 'pt315'), ]
    plotname = 'pvpt315_irot_wind'

    def plot(self, data, static, dateinit, datevalid):
        done = irot_wind.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        overlays=[fig.map_overlay_contour(data['pv','pt315'], static, **conf.plot.merge('pt315', 'pv', 
                contour_labels=False, 
                linewidths=[1.5],
                scale=range(2,3,1) ) ), 
            fig.map_overlay_quiver(data['u_irot','pt315'], data['v_irot','pt315'], static, **conf.plot.merge('pt315', 'u',
                quiver_length=200,
                vector_space_numbers_xy=(45,30), ) ),
        ]
        s=[0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        plotconf = conf.plotf.merge('pt315', 'pv',
                overlays=overlays,
                norm=mpl.colors.BoundaryNorm(s, 256),
                scale=s,
                **self.std_plotconf
        )
        fig.map(data['pv','pt315'], static, **plotconf) 

        return True


# Potential vorticity@350K shading and wind barbs
class pvpt330_wind(irot_wind):
    requires = [('pv', 'pt330'), ('u', 'pt330'), ('v', 'pt330')]
    requires_diagnostic = [(irot_wind.cal_irot_wind, 'pt330'), ]
    plotname = 'pvpt330_irot_wind'

    def plot(self, data, static, dateinit, datevalid):
        done = irot_wind.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        overlays=[fig.map_overlay_contour(data['pv','pt330'], static, **conf.plot.merge('pt330', 'pv', 
                contour_labels=False, 
                linewidths=[1.5],
                scale=range(2,3,1) ) ), 
            fig.map_overlay_quiver(data['u_irot','pt330'], data['v_irot','pt330'], static, **conf.plot.merge('pt330', 'u',
                quiver_length=200,
                vector_space_numbers_xy=(45,30), ) ),
        ]
        s=[0, 1.0,  2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        plotconf = conf.plotf.merge('pt330', 'pv',
                overlays=overlays,
                norm=mpl.colors.BoundaryNorm(s, 256),
                scale=s,
                **self.std_plotconf
        )
        fig.map(data['pv','pt330'], static, **plotconf) 

        return True


# Potential vorticity@315K shading and wind barbs
class pvpt315_wind_npolar(pvpt315_wind,npolar):
    requires = [('pv', 'pt315'), ('u', 'pt315'), ('v', 'pt315')]
    requires_diagnostic = [(irot_wind.cal_irot_wind, 'pt315'), ]
    plotname = 'pvpt315_irot_wind'

    def plot(self, data, static, dateinit, datevalid):
        done = irot_wind.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        overlays=[fig.map_overlay_contour(data['pv','pt315'], static, **conf.plot.merge('pt315', 'pv', 
                contour_labels=False, 
                linewidths=[1.5],
                scale=range(2,3,1) ) ), 
            fig.map_overlay_quiver(data['u_irot','pt315'], data['v_irot','pt315'], static, **conf.plot.merge('pt315', 'u',
                quiver_length=200,
                vector_space_numbers_xy=(45,45), ) ),
        ]
        s=[0, 1.0,  2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        plotconf = conf.plotf.merge('pt315', 'pv',
                overlays=overlays,
                norm=mpl.colors.BoundaryNorm(s, 256),
                scale=s,
                **self.std_plotconf
        )
        fig.map(data['pv','pt315'], static, **plotconf) 

        return True

# Potential vorticity@330K shading and wind barbs
class pvpt330_wind_npolar(pvpt330_wind,npolar):
    requires = [('pv', 'pt330'), ('u', 'pt330'), ('v', 'pt330')]
    requires_diagnostic = [(irot_wind.cal_irot_wind, 'pt330'), ]
    plotname = 'pvpt330_irot_wind'

    def plot(self, data, static, dateinit, datevalid):
        done = irot_wind.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        overlays=[fig.map_overlay_contour(data['pv','pt330'], static, **conf.plot.merge('pt330', 'pv', 
                contour_labels=False, 
                linewidths=[1.5],
                scale=range(2,3,1) ) ), 
            fig.map_overlay_quiver(data['u_irot','pt330'], data['v_irot','pt330'], static, **conf.plot.merge('pt330', 'u',
                quiver_length=200,
                vector_space_numbers_xy=(45,45), ) ),
        ]
        s=[0, 1.0,  2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        plotconf = conf.plotf.merge('pt330', 'pv',
                overlays=overlays,
                norm=mpl.colors.BoundaryNorm(s, 256),
                scale=s,
                **self.std_plotconf
        )
        fig.map(data['pv','pt330'], static, **plotconf) 

        return True

# Potential vorticity@315K shading and wind barbs
class pvpt315_wind_spolar(pvpt315_wind,spolar):
    requires = [('pv', 'pt315'), ('u', 'pt315'), ('v', 'pt315')]
    requires_diagnostic = [(irot_wind.cal_irot_wind, 'pt315'), ]
    plotname = 'pvpt315_irot_wind'

    def plot(self, data, static, dateinit, datevalid):
        done = irot_wind.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        overlays=[fig.map_overlay_contour(data['pv','pt315'], static, **conf.plot.merge('pt315', 'pv', 
                contour_labels=False, 
                linewidths=[1.5],
                hook=lambda pv: -1.0e6*pv,
                scale=range(2,3,1) ) ), 
            fig.map_overlay_quiver(data['u_irot','pt315'], data['v_irot','pt315'], static, **conf.plot.merge('pt315', 'u',
                quiver_length=200,
                vector_space_numbers_xy=(45,45), ) ),
        ]
        s=[0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        st=[0, -1.0, -2.0, -3.0, -4.0, -5.0, -6.0, -7.0, -8.0, -9.0, -10.0]
        plotconf = conf.plotf.merge('pt315', 'pv',
                overlays=overlays,
                norm=mpl.colors.BoundaryNorm(s, 256),
                scale=s,
                ticks=s,
                ticklabels=st,
                hook=lambda pv: -1.0e6*pv,
                **self.std_plotconf
        )
        fig.map(data['pv','pt315'], static, **plotconf) 

        return True


# Potential vorticity@330K shading and wind barbs
class pvpt330_wind_spolar(pvpt330_wind,spolar):
    requires = [('pv', 'pt330'), ('u', 'pt330'), ('v', 'pt330')]
    requires_diagnostic = [(irot_wind.cal_irot_wind, 'pt330'), ]
    plotname = 'pvpt330_irot_wind'

    def plot(self, data, static, dateinit, datevalid):
        done = irot_wind.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        overlays=[fig.map_overlay_contour(data['pv','pt330'], static, **conf.plot.merge('pt330', 'pv', 
                contour_labels=False, 
                linewidths=[1.5],
                hook=lambda pv: -1.0e6*pv,
                scale=range(2,3,1) ) ), 
            fig.map_overlay_quiver(data['u_irot','pt330'], data['v_irot','pt330'], static, **conf.plot.merge('pt330', 'u',
                quiver_length=200,
                vector_space_numbers_xy=(45,45), ) ),
        ]
        s=[0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        st=[0, -1.0, -2.0, -3.0, -4.0, -5.0, -6.0, -7.0, -8.0, -9.0, -10.0]
        plotconf = conf.plotf.merge('pt330', 'pv',
                overlays=overlays,
                norm=mpl.colors.BoundaryNorm(s, 256),
                scale=s,
                ticks=s,
                ticklabels=st,
                hook=lambda pv: -1.0e6*pv,
                **self.std_plotconf
        )
        fig.map(data['pv','pt330'], static, **plotconf) 

        return True


# Potential temperature@PV2 shading and wind barbs
class ptpv2_jets(theta,jets):
    requires = [('t', 'pv2000'), ('p', 'pv2000'), ('u', 'pv2000'), ('v', 'pv2000')]
    requires_diagnostic = [(theta.cal_theta, 'pv2000'), (jets.cal_jetaxis, 'pv2000'), ]
    plotname = 'ptpv2_jets'

    def plot(self, data, static, dateinit, datevalid):
        done = jets.plot(self, data, static, dateinit, datevalid)
        if done:
            return True
        
        overlays = [
            fig.map_overlay_contour(data['ff_smooth','pv2000'], static, **conf.plot.merge('pv2000', 'ff',
                scale=np.arange(30,91,15), 
            ) ),
            fig.map_overlay_lines(data['jetaxis','pv2000'], data['jaoff','pv2000'], static, linecolor='k', linewidth=6), 
            fig.map_overlay_lines(data['jetaxis','pv2000'], data['jaoff','pv2000'], static, linecolor='w', linewidth=4), 
        ]
    
        plotconf = conf.plotf.merge('pv2000', 'pt',
                overlays=overlays,
                scale=np.arange(270,396,5),
                ticks=[270,285,300,315,330,350,370,395],
                **self.std_plotconf
        )
        fig.map(data['pt', 'pv2000'], static, **plotconf)

        return True


# Potential temperature@PV2 shading and wind barbs
class ptpv2_jets_npolar(ptpv2_jets,npolar):
    requires = [('t', 'pv2000'), ('p', 'pv2000'), ('u', 'pv2000'), ('v', 'pv2000')]
    requires_diagnostic = [(theta.cal_theta, 'pv2000'), (jets.cal_jetaxis, 'pv2000'), ]
    plotname = 'ptpv2_jets'


# Potential temperature@PV2 shading and wind barbs
class ptpv2_jets_spolar(ptpv2_jets,spolar):
    requires = [('t', 'pv2000'), ('p', 'pv2000'), ('u', 'pv2000'), ('v', 'pv2000')]
    requires_diagnostic = [(theta.cal_theta, 'pv2000'), (jets.cal_jetaxis, 'pv2000'), ]
    plotname = 'ptpv2_jets'


# Total column water vapour
class tcwv(iwvtrans):
    requires = [('tcwv', 'sfc'), ('crr', 'sfc'), ('lsrr', 'sfc'), 
            ('u', '925'), ('v', '925'), ('rh', '925'), ('t', '925'),
            ('u', '850'), ('v', '850'), ('rh', '850'), ('t', '850'),
            ('u', '700'), ('v', '700'), ('rh', '700'), ('t', '700'),
            ('u', '500'), ('v', '500'), ('rh', '500'), ('t', '500'),
            ('u', '300'), ('v', '300'), ('rh', '300'), ('t', '300'),
    ]
    requires_diagnostic = [(iwvtrans.cal_iwvtransport, ['925', '850', '700', '500', '300']), ]
    plotname = 'tcwv'

    def plot(self, data, static, dateinit, datevalid):
        done = plotter.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        overlays=[fig.map_overlay_contour(data['crr','sfc'], static, **conf.plot.merge('sfc', 'crr',
                scale=[1.0, 3.0, 10.0],
                colors='c', ) ), 
            fig.map_overlay_contour(data['lsrr','sfc'], static, **conf.plot.merge('sfc', 'lsrr',
                scale=[1.0, 3.0, 10.0],
                colors='m', ) ), 
            fig.map_overlay_quiver(data['iwvtransx','sfc'], data['iwvtransy','sfc'], static, 
                **conf.plot.merge('sfc', 'tcwv', linewidths=0.2) ),
            fig.map_overlay_contour(data['t','850'], static, **conf.plot.merge('850', 't',
                linewidths=[1], 
                linestyles='solid',
                colors='firebrick',
                scale=range(-5,-3,2) ) ),
        ]

        plotconf = conf.plotf.merge('sfc', 'tcwv',
                overlays=overlays,
                scale=range(4,51,2),
                ticks=range(10,51,10),
                quiver=True,
                quiver_length=1.5,
                **self.std_plotconf
        )
        fig.map(data['tcwv','sfc'], static, **plotconf)

        return True


# Total column water vapour
class tcwv_perc(percentiles):
    requires = [('tcwv', 'sfc'), ]
    requires_diagnostic = [(percentiles.cal_percentiles, ['tcwv', 'sfc', '1979-2017', ]), ]
    plotname = 'tcwv_perc'

    def plot(self, data, static, dateinit, datevalid):
        done = plotter.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        s = [-30,-25,-21,-18,-15,-13,-11,-9,-7,-5,-3,-1,1,3,5,7,9,11,13,15,18,21,25,30]

        overlays = [
            fig.map_overlay_contour(data['tcwv_percs', 'sfc'], static, plev=None, q='perc', 
                colors='w', scale=[0.5, 18.5]),
            fig.map_overlay_contour(data['tcwv_percs', 'sfc'], static, plev=None, q='perc', 
                colors='0.3', scale=[1.5, 17.5]),
            fig.map_overlay_contour(data['tcwv_percs', 'sfc'], static, plev=None, q='perc', 
                scale=[3.5, 15.5]),
        ]
        plotconf = conf.plotf.merge('sfc', 'tcwv_ano',
                scale=s,
                norm=mpl.colors.BoundaryNorm([-np.inf,]+s+[np.inf,], 256),
                cb_tickspacing='uniform',
                overlays=overlays,
                **self.std_plotconf
        )
        fig.map(data['tcwv_ano', 'sfc'], static, **plotconf)

        return True


# Total column water vapour
class tcwv_npolar(tcwv,npolar):
    requires = [('tcwv', 'sfc'), ('crr', 'sfc'), ('lsrr', 'sfc'), 
            ('u', '925'), ('v', '925'), ('rh', '925'), ('t', '925'),
            ('u', '850'), ('v', '850'), ('rh', '850'), ('t', '850'),
            ('u', '700'), ('v', '700'), ('rh', '700'), ('t', '700'),
            ('u', '500'), ('v', '500'), ('rh', '500'), ('t', '500'),
            ('u', '300'), ('v', '300'), ('rh', '300'), ('t', '300'),
    ]
    requires_diagnostic = [(iwvtrans.cal_iwvtransport, ['925', '850', '700', '500', '300']), ]
    plotname = 'tcwv'

    def plot(self, data, static, dateinit, datevalid):
        done = plotter.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        overlays=[fig.map_overlay_contour(data['crr','sfc'], static, **conf.plot.merge('sfc', 'crr',
                scale=[1.0, 3.0, 10.0],
                colors='c', ) ), 
             fig.map_overlay_contour(data['lsrr','sfc'], static, **conf.plot.merge('sfc', 'lsrr',
                scale=[1.0, 3.0, 10.0],
                colors='m', ) ), 
            fig.map_overlay_quiver(data['iwvtransx','sfc'], data['iwvtransy','sfc'], static, 
                **conf.plot.merge('sfc', 'tcwv', linewidths=0.2) ),
            fig.map_overlay_contour(data['t','850'], static, **conf.plot.merge('850', 't',
                linewidths=[1], 
                linestyles='solid',
                colors='firebrick',
                scale=range(-5,-3,2) ) ),
        ]

        plotconf = conf.plotf.merge('sfc', 'tcwv',
                overlays=overlays,
                scale=range(4,65,2),
                ticks=range(10,61,10),
                quiver=True,
                quiver_length=1.5,
                **self.std_plotconf
        )
        fig.map(data['tcwv','sfc'], static, **plotconf)

        return True


# Total column water vapour
class tcwv_spolar(tcwv,spolar):
    requires = [('tcwv', 'sfc'), ('crr', 'sfc'), ('lsrr', 'sfc'), 
            ('u', '925'), ('v', '925'), ('rh', '925'), ('t', '925'),
            ('u', '850'), ('v', '850'), ('rh', '850'), ('t', '850'),
            ('u', '700'), ('v', '700'), ('rh', '700'), ('t', '700'),
            ('u', '500'), ('v', '500'), ('rh', '500'), ('t', '500'),
            ('u', '300'), ('v', '300'), ('rh', '300'), ('t', '300'),
    ]
    requires_diagnostic = [(iwvtrans.cal_iwvtransport, ['925', '850', '700', '500', '300']), ]
    plotname = 'tcwv'

    def plot(self, data, static, dateinit, datevalid):
        done = plotter.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        overlays=[fig.map_overlay_contour(data['crr','sfc'], static, **conf.plot.merge('sfc', 'crr',
                scale=[1.0, 3.0, 10.0],
                colors='c', ) ), 
             fig.map_overlay_contour(data['lsrr','sfc'], static, **conf.plot.merge('sfc', 'lsrr',
                scale=[1.0, 3.0, 10.0],
                colors='m', ) ), 
            fig.map_overlay_quiver(data['iwvtransx','sfc'], data['iwvtransy','sfc'], static, 
                **conf.plot.merge('sfc', 'tcwv', linewidths=0.2) ),
            fig.map_overlay_contour(data['t','850'], static, **conf.plot.merge('850', 't',
                linewidths=[1], 
                linestyles='solid',
                colors='firebrick',
                scale=range(-5,-3,2) ) ),
        ]

        plotconf = conf.plotf.merge('sfc', 'tcwv',
                overlays=overlays,
                scale=range(4,65,2),
                ticks=range(10,61,10),
                quiver=True,
                quiver_length=1.5,
                **self.std_plotconf
        )
        fig.map(data['tcwv','sfc'], static, **plotconf)

        return True



# Total cloud cover
class cc(plotter):
    requires = [('hcc', 'sfc'), ('mcc', 'sfc'),  ('lcc', 'sfc'), ]
    plotname = 'tcc'

    def plot(self, data, static, dateinit, datevalid):
        done = plotter.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        s = np.array([0,] + list(np.arange(6.25,95,12.5)) + [100,])
        t = (s[1:]+s[:-1])/2.0

        overlays=[fig.map_overlay_shading(data['mcc','sfc'], static, **conf.plotf.merge('sfc', 'mcc',
                alpha=0.5,
                scale=s,
                extend='neither',
                antialiased=True,
                cb_disable=True
            ) ), 
             fig.map_overlay_shading(data['hcc','sfc'], static, **conf.plotf.merge('sfc', 'hcc',
                alpha=0.4, 
                scale=s,
                extend='neither',
                antialiased=True,
                cb_disable=True
            ) ), 
        ]
        plotconf = conf.plotf.merge('sfc', 'lcc',
                overlays=overlays,
                scale=s,
                ticks=t,
                ticklabels=["0/8","1/8", "2/8", "3/8", "4/8", "5/8", "6/8", "7/8", "8/8"],
                extend='neither',
                **self.std_plotconf
        )
        plotconf['coastcolor'] = '0.7'
        fig.map(data['lcc','sfc'], static, **plotconf)

        return True


# Surface fluxes, wind barbs, sea ice 
class sshf_winds(ff10):
    requires = [('u10', 'sfc'), ('v10', 'sfc'), ('sshff', 'sfc'), ('sst', 'sfc'), ('ci', 'sfc'), ]
    requires_diagnostic = [(ff10.cal_ff10, 'sfc'), ]
    plotname = 'sshf_winds'

    def plot(self, data, static, dateinit, datevalid):
        done = plotter.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        shf = [-300,-200,-140,-100,-70,-50,-30,-20,-14,-10, 30,50,70,100,140,200,300,500,700,1000,]
        shft = [-10000,]+shf+[10000,]

        overlays = [
            fig.map_overlay_barbs(data['u10','sfc'], data['v10','sfc'], static, **conf.plot.merge('sfc', 'ff10',
                linewidths=0.5,
                **self.std_plotconf) ),
            fig.map_overlay_contour(data['ff10','sfc'], static, **conf.plot.merge('sfc', 'ff10',
                colors='gold',
                linewidths=[1],
                scale=[17.2, ] ) ),
            fig.map_overlay_contour(data['ff10','sfc'], static, **conf.plot.merge('sfc', 'ff10',
                colors='coral',
                linewidths=[1.5],
                scale=[24.5, ] ) ),
            fig.map_overlay_contour(data['ff10','sfc'], static, **conf.plot.merge('sfc', 'ff10',
                colors='crimson',
                linewidths=[2],
                scale=[32.7, ] ) ),
            fig.map_overlay_contour(data['ci','sfc'], static, **conf.plot.merge('sfc', 'ci',
                colors='royalblue',
                linewidths=[1],
                scale=[0.2, 0.8] ) ),
            fig.map_overlay_contour(data['sst','sfc'], static, **conf.plot.merge('sfc', 'sst',
                colors='k',
                alpha=0.5,
                linewidths=[0.7],
                scale=[2,4,6,8,12,14,16,18,22,24,26,28,32,34] ) ),
            fig.map_overlay_contour(data['sst','sfc'], static, **conf.plot.merge('sfc', 'sst',
                colors='k',
                alpha=0.6,
                linewidths=[1],
                scale=np.arange(0,31,10) ) ),
        ]

        plotconf = conf.plotf.merge('sfc', 'sshff',
                cmap=cm.BrBG,
                scale=shf,
                norm=mpl.colors.BoundaryNorm(shft, 256),
                extend='both',
                cb_tickspacing='uniform',
                overlays=overlays,
                **self.std_plotconf
        )
        fig.map(data['sshff','sfc'], static, **plotconf)

        return True


# Surface fluxes, wind barbs, sea ice 
class slhf_winds(ff10):
    requires = [('u10', 'sfc'), ('v10', 'sfc'), ('slhff', 'sfc'), ('sst', 'sfc'), ('ci', 'sfc'), ]
    requires_diagnostic = [(ff10.cal_ff10, 'sfc'), ]
    plotname = 'slhf_winds'

    def plot(self, data, static, dateinit, datevalid):
        done = plotter.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        shf = [-300,-200,-140,-100,-70,-50,-30,-20,-14,-10, 30,50,70,100,140,200,300,500,700,1000,]
        shft = [-10000,]+shf+[10000,]

        overlays = [
            fig.map_overlay_barbs(data['u10','sfc'], data['v10','sfc'], static, **conf.plot.merge('sfc', 'ff10',
                linewidths=0.5,
                **self.std_plotconf) ),
            fig.map_overlay_contour(data['ff10','sfc'], static, **conf.plot.merge('sfc', 'ff10',
                colors='gold',
                linewidths=[1],
                scale=[17.2, ] ) ),
            fig.map_overlay_contour(data['ff10','sfc'], static, **conf.plot.merge('sfc', 'ff10',
                colors='coral',
                linewidths=[1.5],
                scale=[24.5, ] ) ),
            fig.map_overlay_contour(data['ff10','sfc'], static, **conf.plot.merge('sfc', 'ff10',
                colors='crimson',
                linewidths=[2],
                scale=[32.7, ] ) ),
            fig.map_overlay_contour(data['ci','sfc'], static, **conf.plot.merge('sfc', 'ci',
                colors='royalblue',
                linewidths=[1],
                scale=[0.2, 0.8] ) ),
            fig.map_overlay_contour(data['sst','sfc'], static, **conf.plot.merge('sfc', 'sst',
                colors='k',
                alpha=0.5,
                linewidths=[0.7],
                scale=[2,4,6,8,12,14,16,18,22,24,26,28,32,34] ) ),
            fig.map_overlay_contour(data['sst','sfc'], static, **conf.plot.merge('sfc', 'sst',
                colors='k',
                alpha=0.6,
                linewidths=[1],
                scale=np.arange(0,31,10) ) ),
        ]

        plotconf = conf.plotf.merge('sfc', 'slhff',
                cmap=cm.BrBG,
                scale=shf,
                norm=mpl.colors.BoundaryNorm(shft, 256),
                extend='both',
                cb_tickspacing='uniform',
                overlays=overlays,
                **self.std_plotconf
        )
        fig.map(data['slhff','sfc'], static, **plotconf)

        return True


# Near surface winds.
class deform850_fronts(deform,fronts,spec_hum,precip):
    requires = [('u', '850'), ('v', '850'), 
        ('t', '925'), ('t', '850'), ('t', '700'), 
        ('rh', '925'), ('rh', '850'), ('rh', '700'), 
        ('lsrr', 'sfc'), ('crr', 'sfc'), ('msl', 'sfc'),
    ]
    requires_diagnostic = [(spec_hum.cal_spec_hum, '925'), (spec_hum.cal_spec_hum, '850'),
            (spec_hum.cal_spec_hum, '700'), (precip.cal_trr, 'sfc'),
            (deform.cal_deform, '850'), (fronts.detect_frontalvolumes, '850'), 
            (fronts.detect_frontlines, '850'), ]
    plotname = 'deform850_fronts'

    def plot(self, data, static, dateinit, datevalid):
        done = plotter.plot(self, data, static, dateinit, datevalid)
        if done:
            return True
        
        # Mask areas of weak deformation in the overlay
        defabs, defang = data['defabs','850'], data['defang','850']
        defabs[defabs < 1.0e-4] = np.nan
        defang[defabs < 1.0e-4] = np.nan

        data['t','850'] = dynlib.utils.smooth_xy(data['t','850'][np.newaxis,:,:], 3)[0,:,:]
        data['trr','sfc'] = dynlib.utils.smooth_xy(data['trr','sfc'][np.newaxis,:,:], 3)[0,:,:]


        overlays = [
            fig.map_overlay_shading(data['frovo','850'], static, **conf.plot.merge('850', 'z', 
                colors=['seagreen', ],
                alpha=0.3,
                scale=[0.001, 2.0],
                extend='neither',
                cb_disable=True,) ),
            fig.map_overlay_lines(data['fronts','850'][0,::], data['froff','850'][0,::], static, 
                **conf.plot.merge('850', 'z', linecolor='royalblue') ),
            fig.map_overlay_lines(data['fronts','850'][1,::], data['froff','850'][1,::], static, 
                **conf.plot.merge('850', 'z', linecolor='orangered') ),
            fig.map_overlay_lines(data['fronts','850'][2,::], data['froff','850'][2,::], static, 
                **conf.plot.merge('850', 'z', linecolor='orchid') ),
            fig.map_overlay_contour(data['t','850'], static, **conf.plot.merge('850', 't', 
                scale = [-5,],
                colors='firebrick',
                linestyles='solid',
                linewidths=1, ) ),
            fig.map_overlay_contour(data['trr','sfc'], static, **conf.plot.merge('sfc', 'trr', 
                scale = [1,5,],
                colors='teal',
                linewidths=1, ) ),
            fig.map_overlay_dilatation(defabs, defang, static, **conf.plot.merge('850', 'defabs',
                vector_space_numbers_xy=(54,36)) ),
            fig.map_overlay_contour(data['msl','sfc'], static, **conf.plot.merge('sfc', 'msl', 
                linewidths=[0.5], 
                scale=range(900,1070,5),
                alpha=0.25,) ), 
        ]

        plotconf = conf.plotf.merge('850', 'defabs',
                overlays=overlays,
                scale=np.arange(10,36,5),
                **self.std_plotconf
        )
        fig.map(data['defabs','850'], static, **plotconf)

        return True


# -----------------------------------------------------------------------------

# Everything
PLOTS = {
    'plev': [
        z500_msl(), 
        z500_msl_npolar(),
        z500_msl_spolar(),
        t850_msl(), 
        deform850_fronts(),
        tcwv(),
        tcwv_npolar(),
        tcwv_spolar(),
        t850_perc(),
        tcwv_perc(),
    ], 
    'pv2': [
        ptpv2_jets(),
        ptpv2_jets_npolar(),
        ptpv2_jets_spolar(),
    ],
    'test': [
    ],
    'sfc': [
        cc(),
        sshf_winds(),
        slhf_winds(),
    ],
}

# Suggested separation into parallel plot jobs
# plev: 7 plots, front volume + front line diagnostics
# isentropic: 6 plots, irrot wind diagniostic
# pv2 + sfc: 5 plots, jet axis diagnostic

plots = []
if len(sys.argv) > 1:
    first = 2
    # See if a forecast has been specifid, if not use the most recent that should be there.
    try: 
        forecast = dt.strptime(sys.argv[1], DATEFMT)
    except ValueError:
        forecast = get_current_fc_gfs()
        first = 1
    
    for arg in sys.argv[first:]:
        if arg in PLOTS:
            plots.extend(PLOTS[arg])
            print('Plotting plot set "%s".' % arg)
        else:
            print('Unknown plot set "%s".' % arg)
else:
    forecast = get_current_fc_gfs()

# Override
#forecast = dt(2018,4,6,0)
plot_only_init = False

print('Plotting the GFS %s forecasts' % forecast.strftime('%Y-%m-%d %H'))


if len(plots) == 0:
    print('No (known) plot set specified, plotting all plot sets.')
    for plotset in PLOTS.values():
        plots.extend(plotset)

def get_data_grib(f, plev, q):
    varnames_by_q = {
        'u': 'U component of wind',
        'v': 'V component of wind',
        't': 'Temperature',
        'rh': 'Relative humidity',
        'z': 'Geopotential Height',
        'p': 'Pressure',
        'crr': 'Convective precipitation rate',
        'lsrr': 'Precipitation rate',
        'sshff': 'Sensible heat net flux',
        'slhff': 'Latent heat net flux',
    }

    vals = None

    # Special plevs, eg. PV2, merging PV=2 and PV=-2
    if plev == 'pv2000':
        # Southern hemisphere, PV=-2
        msgs = f.select(name=varnames_by_q[q], typeOfLevel='potentialVorticity', level=2147486)
        vals = msgs[0].values.data
        vals[msgs[0].values.mask] = np.nan
    
        # Northern hemisphere, PV=2, overwrite values whereever not NaN
        msgs = f.select(name=varnames_by_q[q], typeOfLevel='potentialVorticity', level=2)
        vals_ = msgs[0].values.data
        vals_[msgs[0].values.mask] = np.nan
        vals[~np.isnan(vals_)] = vals_[~np.isnan(vals_)]
    
    # Sea level pressure has its own vertical level type in grib
    elif plev == 'sfc' and q == 'msl':
        msgs = f.select(name='MSLP (Eta model reduction)')
    # Precipitiable water has no vertical level type in grib
    elif plev == 'sfc' and q == 'tcwv':
        msgs = f.select(name='Precipitable water')
    elif plev == 'sfc' and q == 'lcc':
        if f[1].forecastTime == 0:
            return np.zeros(f[1].values.shape)
        msgs = f.select(typeOfFirstFixedSurface='214', stepType='instant')
    elif plev == 'sfc' and q == 'mcc':
        if f[1].forecastTime == 0:
            return np.zeros(f[1].values.shape)
        msgs = f.select(typeOfFirstFixedSurface='224', stepType='instant')
    elif plev == 'sfc' and q == 'hcc':
        if f[1].forecastTime == 0:
            return np.zeros(f[1].values.shape)
        msgs = f.select(typeOfFirstFixedSurface='234', stepType='instant')
    elif plev == 'sfc' and  q == 'u10':
        msgs = f.select(name='10 metre U wind component')
    elif plev == 'sfc' and  q == 'v10':
        msgs = f.select(name='10 metre V wind component')
    elif plev == 'sfc' and q == 'sst':
        msgs = f.select(name='Temperature', typeOfLevel='surface')
        vals = msgs[0].values
        msgs = f.select(name='Land-sea mask')
        landmask = msgs[0].values
        vals[landmask == 1] = np.nan
    elif plev == 'sfc' and q == 'ci':
        msgs = f.select(name='Sea ice area fraction', typeOfLevel='surface')
        vals = msgs[0].values
        msgs = f.select(name='Land-sea mask')
        landmask = msgs[0].values
        vals[landmask == 1] = np.nan
    # Surface variables
    elif plev == 'sfc':
        if q in ['crr', 'lsrr', 'sshff', 'slhff'] and f[1].forecastTime == 0:
            return np.zeros(f[1].values.shape)
        msgs = f.select(name=varnames_by_q[q], typeOfLevel='surface', stepType='avg')
    # Standard pressure levels
    else:
        plev = int(plev)
        msgs = f.select(name=varnames_by_q[q], typeOfLevel='isobaricInhPa', level=plev)
    
    if len(msgs) > 1:
        raise ValueError('Found multiple grib messages fitting (%s, %s)' % (q, plev))
    elif len(msgs) < 1:
        raise ValueError('Found no grib messages fitting (%s, %s)' % (q, plev))
    
    # Make possible to set values manually, e.g. for merging PV=2 and PV=-2 levels and constructing SSTs
    if type(vals) == type(None):
        vals = msgs[0].values

    return vals

for lead in get_avail_leads():
    date = forecast + lead * td(0,3600)
    
    fpath = conf.datapath + '/%(time)s/gfs.t%(hour)02dz.pgrb2.0p50.f%(lead)03d' % \
        {'time': forecast.strftime('%Y%m%d%H'), 'hour': forecast.hour, 'lead': lead}
    print(fpath)
    f = pygrib.open(fpath)
    static = grid_by_latlon(*f[1].latlons())
    static.oro = np.zeros((static.ny, static.nx))
    static.t_parsed = [date, ]
    
    data_inst = {}
    for plot in plots:
        plot.error = False
        for q, plev in plot.requires:
            data_inst[q,plev] = get_data_grib(f, plev, q)[np.newaxis,:,:]
            if type(data_inst[q,plev]) == np.ma.MaskedArray:
                dat_ = data_inst[q,plev].data
                dat_[dat_ >= 9.99e+20] = np.nan

        if not plot.error:
            for fun, plev in plot.requires_diagnostic:
                fun(plot, data_inst, plev, static)

    for q,plev in data_inst:
        data_inst[q,plev] = data_inst[q,plev].squeeze()
    
    for plot in plots:
        plot.plot(data_inst, static, forecast, date)
        plt.close()
        

# the end
