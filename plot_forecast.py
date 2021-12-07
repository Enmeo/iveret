#!/usr/bin/env python
# -*- encoding: utf-8

import copy

import matplotlib as mpl
mpl.use('Agg')
from mpl_toolkits.basemap import Basemap

import dynlib
import dynlib.detect
import dynlib.diag
import dynlib.sphere
import dynlib.thermodyn
import dynlib.utils

from dynlib.shorthands import *
from settings.ecmwf import *

from current_fc import *

######################################################
# The base of _everything_

# Genering plot
class plotter(object):
    filetype = 'png'
    fcsrc = 'ec'
    domain = 'natl'
    
    # Add colorbar and legend
    decorations = False

    # Which data is required for the plot
    requires = []
    requires_ens = []
    requires_diagnostic = []
    fmt = '%Y%m%d%H'

    std_plotconf = {
        'm': proj.N_Atlantic_forecast,
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
        self.std_plotconf['save'] = '%s/%s/%s/%s_for_%s.%s' % (
                self.domain, self.plotname, self.fcsrc, 
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


# Base for all northern stereographic maps
class npolar(plotter):
    domain = 'npolar'

    std_plotconf = copy.copy(plotter.std_plotconf)
    std_plotconf['m'] = proj.n_hemisphere_forecast

    figsize = (6.4,6.4)
    figsize_deco = (7.27273,6.4)


# Base for all southern stereographic maps
class spolar(plotter):
    domain = 'spolar'

    std_plotconf = copy.copy(plotter.std_plotconf)
    std_plotconf['m'] = proj.s_hemisphere_forecast

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

# (Integrated) Fluxes
class flux(plotter):
    # From integrated flux to flux (in W/m²)
    def __normalise(self, cum_flux, static):
        dates = static.t_parsed
        intlens = np.array([(dates[i+1]-dates[i]).total_seconds() for i in range(len(dates)-1)])
        flux = np.zeros(cum_flux.shape)
        flux[1:] = cum_flux[1:]-cum_flux[:-1]
        flux[1:] /= intlens[:,np.newaxis,np.newaxis]

        return -1*flux

    def cal_sensible(self, data, plev, static):
        if not ('sshff', plev) in data:
            data['sshff',plev] = dynlib.utils.smooth_xy(
                    self.__normalise(data['sshf',plev], static), 3)

    def cal_latent(self, data, plev, static):
        if not ('slhff', plev) in data:
            data['slhff',plev] = dynlib.utils.smooth_xy(
                    self.__normalise(data['slhf',plev], static), 3)

# Precipitation
class precip(plotter):
    # From cumulative precipitation to precip per hour
    def __normalise(self, cum_precip, static):
        dates = static.t_parsed
        intlens = np.array([(dates[i+1]-dates[i]).total_seconds() for i in range(len(dates)-1)])
        precip = np.zeros(cum_precip.shape)
        precip[1:] = cum_precip[1:]-cum_precip[:-1]
        precip[1:] *= 3600.0 / intlens[:,np.newaxis,np.newaxis]

        return precip

    def cal_crainrate(self, data, plev, static):
        if not ('crr', plev) in data:
            data['crr',plev] = self.__normalise(data['cp',plev], static)

    def cal_lsrainrate(self, data, plev, static):
        if not ('lsrr', plev) in data:
            data['lsrr',plev] = self.__normalise(data['lsp',plev], static)
    
    def cal_trainrate(self, data, plev, static):
        if not ('trr', plev) in data:
            data['trr',plev] = data['crr',plev] + data['lsrr',plev]

# Integrated water vapour constant, based on a given set of pressure levels
class iwvtrans(plotter):
    pbot = 1000
    ptop = 200
    scalefac = (pbot-ptop)*100/9.81
    
    # plevs must be in decending order
    def cal_iwvtransport(self, data, plevs, static):
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
            data['iwvt','sfc'] = np.sqrt(data['iwvtransx','sfc']**2 + data['iwvtransy','sfc']**2) * self.scalefac

        if not ('iwvtaxis','sfc') in data:
            dynfor.config.nsmooth = 0
            dynfor.config.minlen = 2.0e6 
            dynfor.config.jetint_thres = 5.0e-7
            dynfor.config.searchrad = 1.5

            # Interpolation to T84 resolution
            u, conv = dynlib.utils.fill_nan(data['iwvtransx','sfc'])
            v, conv = dynlib.utils.fill_nan(data['iwvtransy','sfc'])
            br, bi, cr, ci = dynlib.sphere.sh_analysis_vector(u, v)
            dynlib.sphere.trunc_triangular(br, bi, 84)
            dynlib.sphere.trunc_triangular(cr, ci, 84)
            iwvtxs, iwvtys = dynlib.sphere.sh_synthesis_vector(data['iwvtransx','sfc'].shape[2], br,bi,cr,ci)
            iwvtxs *= self.scalefac
            iwvtys *= self.scalefac

            # Integrated water vapour transport axis detections
            data['iwvtaxis','sfc'], data['iwvtoff','sfc'] = dynlib.detect.jetaxis(10000, 2000, 
                    iwvtxs, iwvtys, static.dx, static.dy)
            data['iwvtoff','sfc'] = data['iwvtoff','sfc'].astype('i4')


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


# Cyclone masks from ensemble forecasts
class jetdetect_ens(plotter):
    def __init__(self, *args, **kwargs):
        super(*args, **kwargs)

        self.green = None

    def cal_jetaxis(self, data, info, static):
        dynfor.config.nsmooth = 0
        dynfor.config.minlen = 2.0e6 
        dynfor.config.jetint_thres = 0.55e-8
        dynfor.config.searchrad = 1.5

        if not ('jetfreq', plev) in data:
            staticl = data['static_lowres']

            # Precalculate distances between points on a lat/lon grid
            if type(self.green) == type(None):
                self.green = dynlib.utils.dist_green_latlon(staticl.x[0,:], staticl.y[:,0])

            data['jetfreq',plev] = np.empty(data['u',plev,'ens'].shape[0:1]+data['u',plev,'ens'].shape[2:])
            for tidx in range(data['u',plev,'ens'].shape[0]):
                uin = np.concatenate((data['u',plev,'ens'][tidx,:,:,:], data['u',plev,'ensctrl'][tidx:tidx+1,:,:]), axis=0)
                vin = np.concatenate((data['v',plev,'ens'][tidx,:,:,:], data['v',plev,'ensctrl'][tidx:tidx+1,:,:]), axis=0)

                # Jet axis detections
                ja, jaoff = dynlib.detect.jetaxis(10000, 100, uin, vin, staticl.dx, staticl.dy)
                jaoff = jaoff.astype('i4')
                jamask = dynlib.utils.mask_lines(uin.shape[2], uin.shape[1], ja, jaoff)
                
                # Find everything within 300 km of a jet axis and save 
                mindists = dynlib.utils.dist_from_mask_latlon(jamask, self.green, 120)
                data['jetfreq',plev][tidx,:,:] = (mindists < 300.0e3).mean(axis=0)


# Cyclone masks from ensemble forecasts
class cycdetect_ens(plotter):
    def cal_cyclones(self, data, info, static):
        if not ('cycfreq','sfc') in data:
            dynfor.config.cyc_minsize = 0.5e6       # in km^2
            dynfor.config.cyc_maxsize = 4.5e6       # in km^2
            dynfor.config.cyc_maxoro = 1500         # in m
            dynfor.config.cyc_mindist = 750         # in km
            dynfor.config.cyc_minprominence = 200   # in Pa
            
            s = data['msl','sfc','ens'].shape
            data['cycfreq','sfc'] = np.empty(s[0:1]+s[2:])
            indat = np.empty((s[1]+1,)+s[2:])
            for tidx in range(s[0]):
                print(f'{tidx}/{s[0]}')
                indat[0,:,:] = data['msl','sfc','ensctrl'][tidx,:,:]
                indat[1:,:,:] = data['msl','sfc','ens'][tidx,:,:,:]
                cycmask, meta = dynlib.detect.cyclone_by_contour(indat, static)
                cycmask[cycmask > 0.5] = 1
                data['cycfreq','sfc'][tidx,:,:] = cycmask.mean(axis=0)
    
    def cal_ensmean_msl(self, data, info, static):
        if not ('msl','sfc','ensmean') in data:
            data['msl','sfc','ensmean'] = (data['msl','sfc','ens'].sum(axis=1) + data['msl','sfc','ensctrl'])/51.0


# Percentile plots
class percentiles(plotter):
    BASE_PATH = '/home/ubuntu/data'
    conf.datapath.insert(1, BASE_PATH)

    def cal_percentiles(self, data, info, static):
        q, plev, base_period = info
        qp = '%s_percs' % q
        qa = '%s_ano' % q
        if not (qp, plev) in data or not (qa,plev) in data:
            filename = 'ea.ans.%s.%s.%s' % (base_period, plev, qp)
            print('Using base data from %s' % filename)
            f, base_data = metopen(filename, q, no_static=True)
            percs = f.variables['percentile'][:]
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
            fig.map_overlay_contour(data['msl','sfc'], static, **pconfl.merge('sfc', 'msl', 
                linewidths=[0.5], 
                scale=range(900,1070,5),
                alpha=0.8,) ), 
            fig.map_overlay_contour(data['t','850'], static, **pconfl.merge('850', 't',
                linewidths=[1], 
                linestyles='dashed',
                scale=range(0,2,2) ) ),
            fig.map_overlay_barbs(data['u','850'], data['v','850'], static, **pconfl.merge('sfc', 'ff10', 
                alpha=0.5,
                linewidths=0.5,
                length=5,
                **self.std_plotconf) ),
        ]
        plotconf = pconf.merge('850', 't',
                overlays=overlays,
                scale=range(-34,36,2),
                ticks=range(-30,31,10),
                **self.std_plotconf
        )
        fig.map(data['t', '850'], static, **plotconf)

        return True


# Temperature@850hPa shading and MSLP contours
class t850_msl_npolar(t850_msl,npolar):
    requires = [('t', '850'), ('u', '850'), ('v', '850'), ('msl', 'sfc'), ]
    plotname = 't850_msl'

    std_plotconf = npolar.std_plotconf
    std_plotconf['vector_space_numbers_xy'] = (36, 36)


# Temperature@500hPa shading and MSLP contours
class t850_msl_spolar(t850_msl,spolar):
    requires = [('t', '850'), ('u', '850'), ('v', '850'), ('msl', 'sfc'), ]
    plotname = 't850_msl'

    std_plotconf = spolar.std_plotconf
    std_plotconf['vector_space_numbers_xy'] = (36, 36)

    def plot(self, data, static, dateinit, datevalid):
        done = t_msl.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        overlays = [
            fig.map_overlay_contour(data['msl','sfc'], static, **pconfl.merge('sfc', 'msl', 
                linewidths=[0.5], 
                scale=range(900,1070,5),
                alpha=0.8,) ), 
            fig.map_overlay_contour(data['t','850'], static, **pconfl.merge('850', 't',
                linewidths=[1], 
                linestyles='dashed',
                scale=range(0,2,2) ) ),
            # I guess I am triggering a bug somehwere. Otherwise no idea why this would be necessary.
            fig.map_overlay_barbs(-data['u','850'], -data['v','850'], static, **pconfl.merge('sfc', 'ff10', 
                alpha=0.5,
                linewidths=0.5,
                length=5,
                **self.std_plotconf) ),
        ]
        plotconf = pconf.merge('850', 't',
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
    requires_diagnostic = [(percentiles.cal_percentiles, ['t', '850', '1979-2020', ]), ]
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
        plotconf = pconf.merge('850', 't_ano',
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
            fig.map_overlay_contour(data['msl','sfc'], static, **pconfl.merge('sfc','msl',  
                alpha=0.8,
                contour_labels=True, 
                contour_labels_format='%g',
                linewidths=[1], 
                scale=range(900,1070,5) ) ),
            #fig.map_overlay_contour(data['z','500'], static, **pconfl.merge('500', 'z',
            #    contour_labels=True, 
            #    colors='white',
            #    linewidths=[1],
            #    linestyles='dashed',
            #    scale=range(472,601,16) ) ),
            fig.map_overlay_contour(data['z','500'], static, **pconfl.merge('500', 'z',
                contour_labels=False, 
                colors='white',
                linewidths=[2],
                scale=range(552,554,2) ) ), 
        ]
        plotconf = pconf.merge('500', 'z',
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

        overlays=[fig.map_overlay_contour(data['pv','pt315'], static, **pconfl.merge('pt315', 'pv', 
                contour_labels=False, 
                linewidths=[1.5],
                scale=range(2,3,1) ) ), 
            fig.map_overlay_quiver(data['u_irot','pt315'], data['v_irot','pt315'], static, **pconfl.merge('pt315', 'u',
                quiver_length=200,
                vector_space_numbers_xy=(45,30), ) ),
        ]
        s=[0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        plotconf = pconf.merge('pt315', 'pv',
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

        overlays=[fig.map_overlay_contour(data['pv','pt330'], static, **pconfl.merge('pt330', 'pv', 
                contour_labels=False, 
                linewidths=[1.5],
                scale=range(2,3,1) ) ), 
            fig.map_overlay_quiver(data['u_irot','pt330'], data['v_irot','pt330'], static, **pconfl.merge('pt330', 'u',
                quiver_length=200,
                vector_space_numbers_xy=(45,30), ) ),
        ]
        s=[0, 1.0,  2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        plotconf = pconf.merge('pt330', 'pv',
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

        overlays=[fig.map_overlay_contour(data['pv','pt315'], static, **pconfl.merge('pt315', 'pv', 
                contour_labels=False, 
                linewidths=[1.5],
                scale=range(2,3,1) ) ), 
            fig.map_overlay_quiver(data['u_irot','pt315'], data['v_irot','pt315'], static, **pconfl.merge('pt315', 'u',
                quiver_length=200,
                vector_space_numbers_xy=(45,45), ) ),
        ]
        s=[0, 1.0,  2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        plotconf = pconf.merge('pt315', 'pv',
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

        overlays=[fig.map_overlay_contour(data['pv','pt330'], static, **pconfl.merge('pt330', 'pv', 
                contour_labels=False, 
                linewidths=[1.5],
                scale=range(2,3,1) ) ), 
            fig.map_overlay_quiver(data['u_irot','pt330'], data['v_irot','pt330'], static, **pconfl.merge('pt330', 'u',
                quiver_length=200,
                vector_space_numbers_xy=(45,45), ) ),
        ]
        s=[0, 1.0,  2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        plotconf = pconf.merge('pt330', 'pv',
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

        overlays=[fig.map_overlay_contour(data['pv','pt315'], static, **pconfl.merge('pt315', 'pv', 
                contour_labels=False, 
                linewidths=[1.5],
                hook=lambda pv: -1.0e6*pv,
                scale=range(2,3,1) ) ), 
            fig.map_overlay_quiver(data['u_irot','pt315'], data['v_irot','pt315'], static, **pconfl.merge('pt315', 'u',
                quiver_length=200,
                vector_space_numbers_xy=(45,45), ) ),
        ]
        s=[0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        st=[0, -1.0, -2.0, -3.0, -4.0, -5.0, -6.0, -7.0, -8.0, -9.0, -10.0]
        plotconf = pconf.merge('pt315', 'pv',
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

        overlays=[fig.map_overlay_contour(data['pv','pt330'], static, **pconfl.merge('pt330', 'pv', 
                contour_labels=False, 
                linewidths=[1.5],
                hook=lambda pv: -1.0e6*pv,
                scale=range(2,3,1) ) ), 
            fig.map_overlay_quiver(data['u_irot','pt330'], data['v_irot','pt330'], static, **pconfl.merge('pt330', 'u',
                quiver_length=200,
                vector_space_numbers_xy=(45,45), ) ),
        ]
        s=[0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
        st=[0, -1.0, -2.0, -3.0, -4.0, -5.0, -6.0, -7.0, -8.0, -9.0, -10.0]
        plotconf = pconf.merge('pt330', 'pv',
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
class ptpv2_jets(jets):
    requires = [('pt', 'pv2000'), ('u', 'pv2000'), ('v', 'pv2000')]
    requires_diagnostic = [(jets.cal_jetaxis, 'pv2000'), ]
    plotname = 'ptpv2_jets'

    def plot(self, data, static, dateinit, datevalid):
        done = jets.plot(self, data, static, dateinit, datevalid)
        if done:
            return True
        
        overlays = [
            fig.map_overlay_contour(data['ff_smooth','pv2000'], static, **pconfl.merge('pv2000', 'ff',
                scale=np.arange(30,91,15), 
            ) ),
            fig.map_overlay_lines(data['jetaxis','pv2000'], data['jaoff','pv2000'], static, linecolor='k', linewidth=6), 
            fig.map_overlay_lines(data['jetaxis','pv2000'], data['jaoff','pv2000'], static, linecolor='w', linewidth=4), 
        ]
    
        plotconf = pconf.merge('pv2000', 'pt',
                overlays=overlays,
                scale=np.arange(270,396,5),
                ticks=[270,285,300,315,330,350,370,395],
                **self.std_plotconf
        )
        fig.map(data['pt', 'pv2000'], static, **plotconf)

        return True


# Potential temperature@PV2 shading and wind barbs
class ptpv2_jets_npolar(ptpv2_jets,npolar):
    requires = [('pt', 'pv2000'), ('u', 'pv2000'), ('v', 'pv2000')]
    requires_diagnostic = [(jets.cal_ff, 'pv2000'), (jets.cal_jetaxis, 'pv2000'), ]
    plotname = 'ptpv2_jets' 


# Potential temperature@PV2 shading and wind barbs
class ptpv2_jets_spolar(ptpv2_jets,spolar):
    requires = [('pt', 'pv2000'), ('u', 'pv2000'), ('v', 'pv2000')]
    requires_diagnostic = [(jets.cal_ff, 'pv2000'), (jets.cal_jetaxis, 'pv2000'), ]
    plotname = 'ptpv2_jets' 


# Total column water vapour
class tcwv(precip,iwvtrans):
    requires = [('tcwv', 'sfc'), ('cp', 'sfc'), ('lsp', 'sfc'), 
            ('u', '925'), ('v', '925'), ('q', '925'),
            ('u', '850'), ('v', '850'), ('q', '850'), ('t', '850'),
            ('u', '700'), ('v', '700'), ('q', '700'),
            ('u', '500'), ('v', '500'), ('q', '500'),
            ('u', '300'), ('v', '300'), ('q', '300'),
    ]
    requires_diagnostic = [(iwvtrans.cal_iwvtransport, ['925', '850', '700', '500', '300']),
                (precip.cal_crainrate, 'sfc'), 
                (precip.cal_lsrainrate, 'sfc') ]
    plotname = 'tcwv'

    def plot(self, data, static, dateinit, datevalid):
        done = plotter.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        overlays=[fig.map_overlay_contour(data['crr','sfc'], static, **pconfl.merge('sfc', 'crr',
                scale=[1.0, 3.0, 10.0],
                colors='c', ) ), 
            fig.map_overlay_contour(data['lsrr','sfc'], static, **pconfl.merge('sfc', 'lsrr',
                scale=[1.0, 3.0, 10.0],
                colors='orchid', ) ), 
            fig.map_overlay_quiver(data['iwvtransx','sfc'], data['iwvtransy','sfc'], static, 
                **pconfl.merge('sfc', 'tcwv', linewidths=0.2) ),
            fig.map_overlay_contour(data['t','850'], static, **pconfl.merge('850', 't',
                linewidths=[1], 
                linestyles='solid',
                colors='firebrick',
                scale=range(-5,-3,2) ) ),
        ]

        plotconf = pconf.merge('sfc', 'tcwv',
                overlays=overlays,
                scale=range(4,51,2),
                ticks=range(10,51,10),
                quiver=True,
                quiver_length=1.5,
                **self.std_plotconf
        )
        fig.map(data['tcwv','sfc'], static, **plotconf)

        return True


# Total column water vapour transport + axes
class iwvt_axis(precip,iwvtrans):
    requires = [('cp', 'sfc'), ('lsp', 'sfc'), 
            ('u', '925'), ('v', '925'), ('q', '925'),
            ('u', '850'), ('v', '850'), ('q', '850'), ('t', '850'),
            ('u', '700'), ('v', '700'), ('q', '700'),
            ('u', '500'), ('v', '500'), ('q', '500'),
            ('u', '300'), ('v', '300'), ('q', '300'),
    ]
    requires_diagnostic = [(iwvtrans.cal_iwvtransport, ['925', '850', '700', '500', '300']),
                (precip.cal_crainrate, 'sfc'), 
                (precip.cal_lsrainrate, 'sfc') ]
    plotname = 'iwvt_axis'

    def plot(self, data, static, dateinit, datevalid):
        done = plotter.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        overlays=[fig.map_overlay_contour(data['crr','sfc'], static, **pconfl.merge('sfc', 'crr',
                scale=[1.0, 3.0, 10.0],
                colors='c', ) ), 
            fig.map_overlay_contour(data['lsrr','sfc'], static, **pconfl.merge('sfc', 'lsrr',
                scale=[1.0, 3.0, 10.0],
                colors='orchid', ) ), 
            fig.map_overlay_contour(data['t','850'], static, **pconfl.merge('850', 't',
                linewidths=[1], 
                linestyles='solid',
                colors='firebrick',
                scale=range(-5,-3,2) ) ),
            fig.map_overlay_lines(data['iwvtaxis','sfc'], data['iwvtoff','sfc'], static, linecolor='w', linewidth=4), 
            fig.map_overlay_lines(data['iwvtaxis','sfc'], data['iwvtoff','sfc'], static, linecolor='gold', linewidth=2), 
        ]

        plotconf = pconf.merge('sfc', 'tcwv',
                overlays=overlays,
                scale=np.arange(50,951,50),
                ticks=np.arange(200,951,200),
                **self.std_plotconf
        )
        fig.map(data['iwvt','sfc'], static, **plotconf)

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
        plotconf = pconf.merge('sfc', 'tcwv_ano',
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
    requires = [('tcwv', 'sfc'), ('cp', 'sfc'), ('lsp', 'sfc'), 
            ('u', '925'), ('v', '925'), ('q', '925'),
            ('u', '850'), ('v', '850'), ('q', '850'),
            ('u', '700'), ('v', '700'), ('q', '700'),
            ('u', '500'), ('v', '500'), ('q', '500'),
            ('u', '300'), ('v', '300'), ('q', '300'),
    ]
    requires_diagnostic = [(iwvtrans.cal_iwvtransport, ['925', '850', '700', '500', '300']),
                (precip.cal_crainrate, 'sfc'), 
                (precip.cal_lsrainrate, 'sfc') ]
    plotname = 'tcwv'

    def plot(self, data, static, dateinit, datevalid):
        done = plotter.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        overlays=[fig.map_overlay_contour(data['crr','sfc'], static, **pconfl.merge('sfc', 'crr',
                scale=[1.0, 3.0, 10.0],
                colors='c', ) ), 
             fig.map_overlay_contour(data['lsrr','sfc'], static, **pconfl.merge('sfc', 'lsrr',
                scale=[1.0, 3.0, 10.0],
                colors='m', ) ), 
            fig.map_overlay_quiver(data['iwvtransx','sfc'], data['iwvtransy','sfc'], static, 
                **pconfl.merge('sfc', 'tcwv', vector_space_numbers_xy=(36, 36)) ),
            fig.map_overlay_contour(data['t','850'], static, **pconfl.merge('850', 't',
                linewidths=[1], 
                linestyles='solid',
                colors='firebrick',
                scale=range(-5,-3,2) ) ),
        ]

        plotconf = pconf.merge('sfc', 'tcwv',
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
    requires = [('tcwv', 'sfc'), ('cp', 'sfc'), ('lsp', 'sfc'), 
            ('u', '925'), ('v', '925'), ('q', '925'),
            ('u', '850'), ('v', '850'), ('q', '850'),
            ('u', '700'), ('v', '700'), ('q', '700'),
            ('u', '500'), ('v', '500'), ('q', '500'),
            ('u', '300'), ('v', '300'), ('q', '300'),
    ]
    requires_diagnostic = [(iwvtrans.cal_iwvtransport, ['925', '850', '700', '500', '300']),
                (precip.cal_crainrate, 'sfc'), 
                (precip.cal_lsrainrate, 'sfc') ]
    plotname = 'tcwv'

    def plot(self, data, static, dateinit, datevalid):
        done = plotter.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        overlays=[fig.map_overlay_contour(data['crr','sfc'], static, **pconfl.merge('sfc', 'crr',
                scale=[1.0, 3.0, 10.0],
                colors='c', ) ), 
             fig.map_overlay_contour(data['lsrr','sfc'], static, **pconfl.merge('sfc', 'lsrr',
                scale=[1.0, 3.0, 10.0],
                colors='m', ) ), 
            fig.map_overlay_quiver(data['iwvtransx','sfc'], data['iwvtransy','sfc'], static, 
                **pconfl.merge('sfc', 'tcwv', vector_space_numbers_xy=(36, 36)) ),
            fig.map_overlay_contour(data['t','850'], static, **pconfl.merge('850', 't',
                linewidths=[1], 
                linestyles='solid',
                colors='firebrick',
                scale=range(-5,-3,2) ) ),
        ]

        plotconf = pconf.merge('sfc', 'tcwv',
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

        s = np.array([0,] + list(np.arange(0.0625,0.95,0.125)) + [1,])
        t = (s[1:]+s[:-1])/2.0

        overlays=[fig.map_overlay_shading(data['mcc','sfc'], static, **pconf.merge('sfc', 'mcc',
                alpha=0.5,
                scale=s,
                extend='neither',
                antialiased=True,
                cb_disable=True
            ) ), 
             fig.map_overlay_shading(data['hcc','sfc'], static, **pconf.merge('sfc', 'hcc',
                alpha=0.4, 
                scale=s,
                extend='neither',
                antialiased=True,
                cb_disable=True
            ) ), 
        ]
        plotconf = pconf.merge('sfc', 'lcc',
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
class sshf_winds(ff10,flux):
    requires = [('u10', 'sfc'), ('v10', 'sfc'), ('sshf', 'sfc'), ('sst', 'sfc'), ('siconc', 'sfc'), ]
    requires_diagnostic = [(ff10.cal_ff10, 'sfc'), (flux.cal_sensible, 'sfc'), ]
    plotname = 'sshf_winds'

    def plot(self, data, static, dateinit, datevalid):
        done = plotter.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        shf = [-300,-200,-140,-100,-70,-50,-30,-20,-14,-10, 30,50,70,100,140,200,300,500,700,1000,]
        shft = [-10000,]+shf+[10000,]

        overlays = [
            fig.map_overlay_barbs(data['u10','sfc'], data['v10','sfc'], static, **pconfl.merge('sfc', 'ff10',
                linewidths=0.5,
                **self.std_plotconf) ),
            fig.map_overlay_contour(data['ff10','sfc'], static, **pconfl.merge('sfc', 'ff10',
                colors='gold',
                linewidths=[1],
                scale=[17.2, ] ) ),
            fig.map_overlay_contour(data['ff10','sfc'], static, **pconfl.merge('sfc', 'ff10',
                colors='coral',
                linewidths=[1.5],
                scale=[24.5, ] ) ),
            fig.map_overlay_contour(data['ff10','sfc'], static, **pconfl.merge('sfc', 'ff10',
                colors='crimson',
                linewidths=[2],
                scale=[32.7, ] ) ),
            fig.map_overlay_contour(data['siconc','sfc'], static, **pconfl.merge('sfc', 'siconc',
                colors='royalblue',
                linewidths=[1],
                scale=[0.2, 0.8] ) ),
            fig.map_overlay_contour(data['sst','sfc'], static, **pconfl.merge('sfc', 'sst',
                colors='k',
                alpha=0.5,
                linewidths=[0.7],
                scale=[2,4,6,8,12,14,16,18,22,24,26,28,32,34] ) ),
            fig.map_overlay_contour(data['sst','sfc'], static, **pconfl.merge('sfc', 'sst',
                colors='k',
                alpha=0.6,
                linewidths=[1],
                scale=np.arange(0,31,10) ) ),
        ]

        plotconf = pconf.merge('sfc', 'sshf',
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
class slhf_winds(ff10,flux):
    requires = [('u10', 'sfc'), ('v10', 'sfc'), ('slhf', 'sfc'), ('sst', 'sfc'), ('siconc', 'sfc'), ]
    requires_diagnostic = [(ff10.cal_ff10, 'sfc'), (flux.cal_latent, 'sfc'), ]
    plotname = 'slhf_winds'

    def plot(self, data, static, dateinit, datevalid):
        done = plotter.plot(self, data, static, dateinit, datevalid)
        if done:
            return True

        shf = [-300,-200,-140,-100,-70,-50,-30,-20,-14,-10, 30,50,70,100,140,200,300,500,700,1000,]
        shft = [-10000,]+shf+[10000,]

        overlays = [
            fig.map_overlay_barbs(data['u10','sfc'], data['v10','sfc'], static, **pconfl.merge('sfc', 'ff10',
                linewidths=0.5,
                **self.std_plotconf) ),
            fig.map_overlay_contour(data['ff10','sfc'], static, **pconfl.merge('sfc', 'ff10',
                colors='gold',
                linewidths=[1],
                scale=[17.2, ] ) ),
            fig.map_overlay_contour(data['ff10','sfc'], static, **pconfl.merge('sfc', 'ff10',
                colors='coral',
                linewidths=[1.5],
                scale=[24.5, ] ) ),
            fig.map_overlay_contour(data['ff10','sfc'], static, **pconfl.merge('sfc', 'ff10',
                colors='crimson',
                linewidths=[2],
                scale=[32.7, ] ) ),
            fig.map_overlay_contour(data['siconc','sfc'], static, **pconfl.merge('sfc', 'siconc',
                colors='royalblue',
                linewidths=[1],
                scale=[0.2, 0.8] ) ),
            fig.map_overlay_contour(data['sst','sfc'], static, **pconfl.merge('sfc', 'sst',
                colors='k',
                alpha=0.5,
                linewidths=[0.7],
                scale=[2,4,6,8,12,14,16,18,22,24,26,28,32,34] ) ),
            fig.map_overlay_contour(data['sst','sfc'], static, **pconfl.merge('sfc', 'sst',
                colors='k',
                alpha=0.6,
                linewidths=[1],
                scale=np.arange(0,31,10) ) ),
        ]

        plotconf = pconf.merge('sfc', 'slhf',
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
class deform850_fronts(deform,fronts,precip):
    requires = [('u', '850'), ('v', '850'), 
        ('t', '925'), ('t', '850'), ('t', '700'), 
        ('q', '925'), ('q', '850'), ('q', '700'), 
        ('lsp', 'sfc'), ('cp', 'sfc'), ('msl', 'sfc'),
    ]
    requires_diagnostic = [(deform.cal_deform, '850'), (fronts.detect_frontalvolumes, '850'), 
            (fronts.detect_frontlines, '850'), (precip.cal_crainrate, 'sfc'),
            (precip.cal_lsrainrate, 'sfc'), (precip.cal_trainrate, 'sfc'), ]
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
            fig.map_overlay_shading(data['frovo','850'], static, **pconfl.merge('850', 'z', 
                colors=['seagreen', ],
                alpha=0.3,
                scale=[0.001, 2.0],
                extend='neither',
                cb_disable=True,) ),
            fig.map_overlay_lines(data['fronts','850'][0,::], data['froff','850'][0,::], static, 
                **pconfl.merge('850', 'z', linecolor='royalblue') ),
            fig.map_overlay_lines(data['fronts','850'][1,::], data['froff','850'][1,::], static, 
                **pconfl.merge('850', 'z', linecolor='orangered') ),
            fig.map_overlay_lines(data['fronts','850'][2,::], data['froff','850'][2,::], static, 
                **pconfl.merge('850', 'z', linecolor='orchid') ),
            fig.map_overlay_contour(data['t','850'], static, **pconfl.merge('850', 't', 
                scale = [-5,],
                colors='firebrick',
                linestyles='solid',
                linewidths=1, ) ),
            fig.map_overlay_contour(data['trr','sfc'], static, **pconfl.merge('sfc', 'trr', 
                scale = [1,5,],
                colors='teal',
                linewidths=1, ) ),
            fig.map_overlay_dilatation(defabs, defang, static, **pconfl.merge('850', 'defabs',
                vector_space_numbers_xy=(54,36)) ),
            fig.map_overlay_contour(data['msl','sfc'], static, **pconfl.merge('sfc', 'msl', 
                linewidths=[0.5], 
                scale=range(900,1070,5),
                alpha=0.25,) ), 
        ]

        plotconf = pconf.merge('850', 'defabs',
                overlays=overlays,
                scale=np.arange(10,36,5),
                **self.std_plotconf
        )
        fig.map(data['defabs','850'], static, **plotconf)

        return True


class cycfreq_msl(cycdetect_ens):
    requires = []
    requires_ens = [('msl', 'sfc'), ]
    requires_diagnostic = [(cycdetect_ens.cal_ensmean_msl, 'sfc'), (cycdetect_ens.cal_cyclones, 'sfc'), ]
    plotname = 'cycfreq_msl'


    def plot(self, data, static, dateinit, datevalid):
        done = plotter.plot(self, data, static, dateinit, datevalid)
        if done:
            return True
        
        overlays = [
            fig.map_overlay_contour(data['msl','sfc','ensctrl'], static, **pconfl.merge('sfc', 'msl', 
                linewidths=[0.5], 
                scale=range(900,1070,5),
                alpha=0.4,) ), 
            fig.map_overlay_contour(data['msl','sfc','ensmean'], static, **pconfl.merge('sfc', 'msl', 
                linewidths=[0.5,], 
                colors='tab:orange',
                scale=range(900,1070,5),
                alpha=0.7,) ), 
        ]

        plotconf = pconf.merge(None, None,
                cmap='Blues',
                overlays=overlays,
                scale=np.arange(0,1.01,0.05),
                ticks=np.arange(0,1.01,0.2),
                ticklabels=range(0,101,20),
                extend='neither',
                **self.std_plotconf
        )
        fig.map(data['cycfreq','sfc'], static, **plotconf)

        return True


class cycfreq_msl_npolar(cycfreq_msl,npolar):
    requires = []
    requires_ens = [('msl', 'sfc'), ]
    requires_diagnostic = [(cycdetect_ens.cal_cyclones, 'sfc'), ]
    plotname = 'cycfreq_msl'


class cycfreq_msl_spolar(cycfreq_msl,spolar):
    requires = []
    requires_ens = [('msl', 'sfc'), ]
    requires_diagnostic = [(cycdetect_ens.cal_cyclones, 'sfc'), ]
    plotname = 'cycfreq_msl'



class jetfreq_msl(jetdetect_ens, cycdetect_ens):
    requires = []
    requires_ens = [('u', 'pv2000'), ('v', 'pv2000'), ('msl', 'sfc'), ]
    requires_diagnostic = [(cycdetect_ens.cal_ensmean_msl, 'sfc'), (jetdetect_ens.cal_jetaxis, 'pv2000'), ]
    plotname = 'jetfreq_msl'


    def plot(self, data, static, dateinit, datevalid):
        done = plotter.plot(self, data, static, dateinit, datevalid)
        if done:
            return True
        
        overlays = [
            fig.map_overlay_contour(data['msl','sfc','ensctrl'], static, **pconfl.merge('sfc', 'msl', 
                linewidths=[0.5], 
                scale=range(900,1070,5),
                alpha=0.4,) ), 
            fig.map_overlay_contour(data['msl','sfc','ensmean'], static, **pconfl.merge('sfc', 'msl', 
                linewidths=[0.5,], 
                colors='tab:orange',
                scale=range(900,1070,5),
                alpha=0.7,) ), 
        ]

        plotconf = pconf.merge(None, None,
                cmap='Blues',
                overlays=overlays,
                scale=np.arange(0,1.01,0.05),
                ticks=np.arange(0,1.01,0.2),
                ticklabels=range(0,101,20),
                extend='neither',
                **self.std_plotconf
        )
        fig.map(data['jetfreq','pv2000'], data['static_lowres'], **plotconf)

        return True


class jetfreq_msl_npolar(jetfreq_msl,npolar):
    requires = []
    requires_ens = [('u', 'pv2000'), ('v', 'pv2000'), ('msl', 'sfc'), ]
    requires_diagnostic = [(cycdetect_ens.cal_ensmean_msl, 'sfc'), (jetdetect_ens.cal_jetaxis, 'pv2000'), ]
    plotname = 'jetfreq_msl'


class jetfreq_msl_spolar(jetfreq_msl,spolar):
    requires = []
    requires_ens = [('u', 'pv2000'), ('v', 'pv2000'), ('msl', 'sfc'), ]
    requires_diagnostic = [(cycdetect_ens.cal_ensmean_msl, 'sfc'), (jetdetect_ens.cal_jetaxis, 'pv2000'), ]
    plotname = 'jetfreq_msl'


# -----------------------------------------------------------------------------

forecast = get_current_fc()
# Override
#forecast = dt(2019,12,10,0)
plot_only_init = False
fcstr = forecast.strftime(plotter.fmt)

print('Plotting the ECMWF %s forecasts' % forecast.strftime('%Y-%m-%d %H'))

# Everything
PLOTS = {
    'plev': [
#        z500_msl(), 
#        z500_msl_npolar(),
#        z500_msl_spolar(),
#        t850_msl(), 
#        t850_msl_npolar(),
#        t850_msl_spolar(),
        deform850_fronts(),
#        tcwv(),
#        tcwv_npolar(),
#        tcwv_spolar(),
        iwvt_axis(),
        t850_perc(),
#        tcwv_perc(),
    ], 
    'isentropic': [
        pvpt315_wind(),
        pvpt330_wind(),
        pvpt315_wind_npolar(),
        pvpt330_wind_npolar(),
        pvpt315_wind_spolar(),
        pvpt330_wind_spolar(),
    ],
    'pv2': [
        ptpv2_jets(),
        ptpv2_jets_npolar(),
        ptpv2_jets_spolar(),
    ],
    'ens': [
        cycfreq_msl(),
        cycfreq_msl_npolar(),
        cycfreq_msl_spolar(),
        jetfreq_msl(),
        jetfreq_msl_npolar(),
        jetfreq_msl_spolar(),
    ],
    'test': [
        t850_perc(),
    ],
    'sfc': [
        cc(),
        sshf_winds(),
        slhf_winds(),
    ],
}

import sys

# Suggested separation into parallel plot jobs
# plev: 7 plots, front volume + front line diagnostics
# isentropic: 6 plots, irrot wind diagniostic
# pv2 + sfc: 5 plots, jet axis diagnostic

plots = []
if len(sys.argv) > 1:
    for arg in sys.argv[1:]:
        if arg in PLOTS:
            plots.extend(PLOTS[arg])
            print('Plotting plot set "%s".' % arg)
        else:
            print('Unknown plot set "%s".' % arg)
if len(plots) == 0:
    print('No (known) plot set specified, plotting all plot sets.')
    for plotset in PLOTS.values():
        plots.extend(plotset)

if plot_only_init:
    datemask = np.zeros((53,), dtype='bool')
    datemask[0:2] = True
else:
    datemask = np.ones((53,), dtype='bool')

data = {}
for plot in plots:
    plot.error = False
    for q, plev in plot.requires:
        if (q,plev) not in data:
            f, dat_, static = metopen(f'{fcstr}/ec.for.{fcstr}.{plev}.{q}', q)

            data[q,plev] = dat_.squeeze()
            f.close()

    for q, plev in plot.requires_ens:
        if (q,plev,'ens') not in data:
            f, dat_, static_ = metopen(f'{fcstr}/ec.ens.{fcstr}.{plev}.{q}', q)
            data[q,plev,'ens'] = dat_.squeeze()

            f, dat_, static_ = metopen(f'{fcstr}/ec.ensctrl.{fcstr}.{plev}.{q}', q)
            data[q,plev,'ensctrl'] = dat_.squeeze()

            f.close()
        
        # u/v on PV2 are downloaded at 1.5-deg grid prefiltered to T84 resolution
        if static_.dx.shape[1] == 720:
            static = static_
        else:
            data['static_lowres'] = static_
    
    if len(static.t_parsed) > datemask.sum():
        for key in data:
            if type(data[key]) == np.ndarray:
                data[key] = data[key][datemask,...]
        static.t_parsed = static.t_parsed[datemask]

    if not plot.error:
        for fun, plev in plot.requires_diagnostic:
            fun(plot, data, plev, static)


import time

for tidx, date in zip(range(len(static.t)), static.t_parsed):
    data_inst = {}
    for key in data:
        if type(data[key]) == np.ndarray:
            data_inst[key] = data[key][tidx]
        else:
            data_inst[key] = data[key]
    
    for plot in plots:
        plot.plot(data_inst, static, forecast, date)
        plt.close()
        
        # Temporarily delaying the plotting, to hopefully avoid random and obscure Permission denied errors.
        #time.sleep(0.5)


# the end
