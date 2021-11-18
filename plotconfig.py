#!/usr/bin/env python
# -*- encoding: utf-8


import copy
import matplotlib as mpl

from dynlib.shorthands import *
from settings.common2 import pconf, pconfl


#
# Central plot configuration for (hopefully soon) all plots on iveret
#

# Abstract definition of entities and their properties
class domain(object):
    def __init__(self, proj, fig_size, fig_size_deco, **plotconf):
        self.proj = proj
        self.fig_size = fig_size
        self.fig_size_deco = fig_size_deco
        self.plotconf = plotconf

        return

class variable(object):
    def __init__(self, name, units, level='', addinfo=''):
        self.name = name
        self.units = units
        self.level = level
        self.addinfo = addinfo

class plot(object):
    def __init__(self, shading, overlays=[], name=None, **plotconf):
        self.shading = shading
        self.overlays = overlays
        self.plotconf = plotconf
        
        if name:
            self.name = name
        elif self.shading.level:
            self.name = '%s on %s' % (self.shading.name, self.shading.level)
        else:
            self.name = self.shading.name

class overlay(object):
    def __init__(self, colorlabel, variable, contours, otype='contour', **plotconf):
        self.colorlabel = colorlabel
        self.plotconf = plotconf
        self.var = variable
        self.contours = contours
        self.otype = otype
        
        if type(contours) == list:
            self.contour_label = ', '.join(map(str, contours))
        elif type(contours) == range:
            self.contour_label = contours.step
        elif type(contours) == type(None):
            self.contour_label = None
        else:
            raise ValueError(f'Unknown type of contour specification, `{type(contours)}`.')

# Defining data sources
datasources = ['no', 'ecmwf', 'noaa', 'no_kyst', ]

# Defining domains
domains = {
    'npolar': domain(
        lambda: Basemap(projection='npstere',boundinglat=10,lon_0=-50,resolution='c', area_thresh=10000),
        (6.4,6.4), (7.27273,6.4)
    ),
    'spolar': domain(proj.s_hemisphere, (6.4,6.4), (7.27273,6.4)),
    'natl': domain(proj.N_Atlantic_forecast, (7.2,4.8), (8.18182,4.8)),
    'scandes': domain(proj.Scandinavia, (5.5,6.18), (6.25,6.18), vector_space_interval=30, vector_space_numbers_xy=(30,40)),
    'snorway': domain(proj.S_Norway, (6.4,6.4), (7.27273,6.4), vector_space_interval=10),
    'vestland': domain(proj.Vestland, (6.4,6.4), (7.27273,6.4), vector_space_interval=5),
    'barents': domain(proj.Barents_Sea, (5.0,6.375), (5.68182,6.375)),
}

# Defining variables
variables = {
    'z500': variable('Geopotential', 'gpdm', '500 hPa'),
    't850': variable('Temperature', '°C', '850 hPa'),
    't925': variable('Temperature', '°C', '925 hPa'),
    'q850': variable('Specific humidity', 'g/kg', '850 hPa'),
    'q925': variable('Specific humidity', 'g/kg', '925 hPa'),
    'def850': variable('Deformation', '10⁻⁵/s', '850 hPa'),
    't2': variable('2m Temperature', '°C', ''),
    'rh2': variable('2m Relative humidity', '%', ''),
    'ff10': variable('10m Wind speed', 'm/s', ''),
    'tcwv': variable('Total column water vapour', 'kg/m²', ''),
    'lcc': variable('Low cloud cover', '', ''),
    'mcc': variable('Mid-level cloud cover', '', ''),
    'hcc': variable('High cloud cover', '', ''),
    'pvpt315': variable('Potential vorticity', 'PV', '315 K'),
    'pvpt330': variable('Potential vorticity', 'PV', '330 K'),
    'ptpv2': variable('Potential temperature', 'K', 'PV 2'),
    'w850': variable('Vertical wind', 'm/s', '850 hPa'),
    'w500': variable('Vertical wind', 'm/s', '500 hPa'),
    'w700': variable('Vertical wind', 'm/s', '700 hPa'),
    'clba': variable('Cloud base altitude', 'm', ''),
    'sthff': variable('Surface total heat flux', 'W/m²', ''),
    'sshff': variable('Surface sensible heat flux', 'W/m²', ''),
    'slhff': variable('Surface latent heat flux', 'W/m²', ''),

    'tcwvp': variable('Total column water vapour percentiles', '', '', 'based on ERA-Interim 1979-2017'),
    'tcwva': variable('Total column water vapour anomaly', 'kg/m²', '', 'based on ERA-Interim 1979-2017'),
    't850p': variable('Temperature percentiles', '', '850 hPa', 'based on ERA-Interim 1979-2017'),
    't850a': variable('Temperature anomaly', 'K', '850 hPa', 'based on ERA-Interim 1979-2017'),

    'msl': variable('Sea-level pressure', 'hPa', ''),
    'mslc': variable('Ensemble ctrl sea level pressure', 'hPa', ''),
    'mslm': variable('Ensemble mean sea level pressure', 'hPa', ''),
    'cp': variable('Convective precipitation', 'mm/h', ''),
    'lp': variable('Large-scale precipitation', 'mm/h', ''),
    'tp': variable('Total precipitation', 'mm/h', ''),
    'sic': variable('Sea ice concentration', '', ''),
    'sst': variable('Sea-surface temperature', '°C', ''),
    'cycfreq': variable('Cyclone occurrence', '%', ''),
    'jetfreq': variable('Jet occurrence within 300 km', '%', ''),
    'frovo850': variable('Frontal volumes', '', '850 hPa'),
    'fronts850': variable('Front lines', '', '850 hPa'),
    'barbs10': variable('10m Wind barbs', 'm/s', ''),
    'barbs500': variable('Wind barbs', 'm/s', '500 hPa'),
    'barbs700': variable('Wind barbs', 'm/s', '700 hPa'),
    'barbs850': variable('Wind barbs', 'm/s', '850 hPa'),
    'barbs925': variable('Wind barbs', 'm/s', '925 hPa'),
    'ff925': variable('Wind speed', 'm/s', '925 hPa'),
    'caoidx': variable('Cold-air outbreak index', 'K', ''),
    'irbarbspt315': variable('Irrot. wind barbs', 'm/s', '315 K'),
    'irbarbspt330': variable('Irrot. wind barbs', 'm/s', '330 K'),
    'ffpv2': variable('Wind speed', 'm/s', 'PV 2'),
    'defang850': variable('Axes of dilatation', '', '850 hPa'),
    'iwvt': variable('Column integral water vapour transport', 'kg m/s', ''),
    'iwvtaxes': variable('Water vapour transport axes', '', ''),
    'jetaxespv2': variable('Jet axes', '', 'PV 2'),
}
# Make variables available as local variables as well
g = globals()
for v, vdef in variables.items():
    g[v] = vdef
del g

# Define shorthand for overlays used below
o = overlay

# Defining plots
def mask_between_factory(vmin=None, vmax=None):
    if type(vmin) == type(None) and type(vmax) == type(None):
        raise ValueError('Either vmin or vmax must be given.')

    if type(vmin) == type(None):
        def mask_between(dat):
            dat[dat < vmax] = np.nan
            return dat

    elif type(vmax) == type(None):
        def mask_between(dat):
            dat[dat > vmin] = np.nan
            return dat

    else:
        def mask_between(dat):
            mask = np.logical_and(dat > vmin, dat < vmax)
            dat[mask] = np.nan
            return dat

    return mask_between


wl_scale = [-10,-3,-1,-0.3,-0.1,0.1,0.3,1.0,3,10.0]
wl_ticks = [-100,]+wl_scale+[100,]
w_scale = [-10,-5,-3,-2,-1,-0.5,-0.3,-0.2,-0.1,0.1,0.2,0.3,0.5,1,2,3,5,10]
w_ticks = [-100,]+w_scale+[100,]

rh_scale = [0.2, 0.4, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.99]
rh_ticks = [-1,] + rh_scale + [10.0,]

tp_scale = [-1, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.4, 2.0, 3.0, 5.0, 7.0, 10.0]
tp_labels = [0.0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.4, 2.0, 3.0, 5.0, 7.0, 10.0]
tp_ticks = [-1, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.4, 2.0, 3.0, 5.0, 7.0, 10.0, 1000.0]

clba_scale = [0,100,200,300,400,500,750,1000,1250,1500,2000,2500,3000,4000,5000,6000,7000,8000,30000]
clba_ticks = [0, 200, 500, 1000, 1500, 3000, 5000, 8000]

shf_scale = [-300,-200,-140,-100,-70,-50,-30,-20,-14,-10, 30,50,70,100,140,200,300,500,700,1000]
shf_ticks = [-10000,]+shf_scale+[10000,]

# Defining what is available per plot domain and data source

plot_archetypes = {
    't2m_msl': plot(t2, scale=range(-34,36,2), ticks=range(-30,31,10), overlays=[
            o('black dashes', t2, [0,], linestyles='dashed'),
            o('black', msl, range(900,1070,2), contour_labels=True, contour_labels_format='%1.0f'),
        ], name='2m Temperature and SLP'),
    't925_msl': plot(t925, scale=range(-34,36,2), ticks=range(-30,31,10), overlays=[
            o('black dashes', t925, [0,], linestyles='dashed'),
            o('black', msl, range(900,1070,2), contour_labels=True, contour_labels_format='%1.0f'),
            o('black', barbs925, None, otype='barbs', alpha=0.5, linewidths=0.5, length=5),
        ], name='925 hPa Temperature, SLP and wind barbs'),
    't850_msl': plot(t850, scale=range(-34,36,2), ticks=range(-30,31,10), overlays=[
            o('black dashes', t850, [0,], linestyles='dashed'),
            o('black', msl, range(900,1070,2), contour_labels=True, contour_labels_format='%1.0f'),
            o('black', barbs850, None, otype='barbs', alpha=0.5, linewidths=0.5, length=5),
        ], name='850 hPa Temperature, SLP and wind barbs'),
    'q925_msl': plot(q925, scale=np.arange(1,12.1,0.5), ticks=np.arange(2,12.1,2), overlays=[
            o('dark red', t850, [-5,], colors='firebrick', linestyles='solid'),
            o('black', msl, range(900,1070,2), contour_labels=True, contour_labels_format='%1.0f'),
            o('black', barbs925, None, otype='barbs', alpha=0.5, linewidths=0.5, length=5),
    ], name='925 hPa Specific humidity, SLP and wind barbs'),
    'q850_msl': plot(q850, scale=np.arange(1,12.1,0.5), ticks=np.arange(2,12.1,2), overlays=[
            o('dark red', t850, [-5,], colors='firebrick', linestyles='solid'),
            o('black', msl, range(900,1070,2), contour_labels=True, contour_labels_format='%1.0f'),
            o('black', barbs850, None, otype='barbs', alpha=0.5, linewidths=0.5, length=5),
    ], name='850 hPa Specific humidity, SLP and wind barbs'),
    'w850_ff': plot(ff925, scale=range(5,51,5), cmap='Blues', overlays=[
            o('grey-red shading', w850, wl_scale, otype='shading',
                hook=mask_between_factory(-0.1, 0.1), ticks=wl_ticks, norm=mpl.colors.BoundaryNorm(wl_ticks, 256),
                alpha=0.7, cb_tickspacing='uniform', cmap='RdGy_r'),
            o(None, ff925, range(5,51,5), colors=['tab:blue',], linewidths=[0],
                contour_labels=True, contour_label_format='%1.0f'),
    ], name='850 hPa Vertical wind and 925 hPa wind speed'),
    'w500_winds': plot(w500, scale=w_scale, ticks=w_ticks, norm=mpl.colors.BoundaryNorm(w_ticks, 256),
        cb_tickspacing='uniform', cmap='RdGy_r', overlays=[
            o('black', barbs500, None, otype='barbs', alpha=0.5, linewidths=0.5, length=5),
    ], name='500 hPa Vertical wind and wind barbs'),
    'w700_winds': plot(w700, scale=w_scale, ticks=w_ticks, norm=mpl.colors.BoundaryNorm(w_ticks, 256),
        cb_tickspacing='uniform', cmap='RdGy_r', overlays=[
            o('black', barbs700, None, otype='barbs', alpha=0.5, linewidths=0.5, length=5),
    ], name='700 hPa Vertical wind and wind barbs'),
    'ff10_caos': plot(ff10, scale=np.arange(5.0,32.6,2.5), overlays=[
            o('blue', caoidx, [2, 4, 8, 12,], linewidths=[0.9, 1.5, 1.2, 1.2, ], colors='darkblue'),
            o('black', barbs10, None, otype='barbs', alpha=0.5, linewidths=0.5, length=5),
    ], name='10m wind speed, barbs and CAO index'),
    'rh2m_tp': plot(rh2, scale=rh_scale, cmap='Greys_r', ticks=rh_ticks, norm=mpl.colors.BoundaryNorm(rh_ticks, 256), overlays=[
            o('blue shading', tp, tp_scale, otype='shading', alpha=0.5, ticks=tp_ticks, extend='max', ticklabels=tp_labels,
                cb_tickspacing='uniform', norm=mpl.colors.BoundaryNorm(tp_ticks, 256)),
            o('dark red', t850, [-5,], colors='firebrick', linestyles='solid'),
    ], name='2m Relative humidity and precipitation'),
    'clba_msl': plot(clba, scale=clba_scale[:-1], ticks=clba_ticks, cmap='cividis', norm=mpl.colors.BoundaryNorm(clba_scale, 256),
        cb_tickspacing='uniform', extend='max', overlays=[
            o('black', msl, range(900,1070,2), contour_labels=True, contour_labels_format='%1.0f'),
    ], name='Cloud base altitude and SLP'),
    'shf_winds': plot(sthff, scale=shf_scale, cmap='BrBG', norm=mpl.colors.BoundaryNorm(shf_ticks, 256),
        cb_tickspacing='uniform', overlays=[
            o('black', barbs10, None, otype='barbs', alpha=0.5, linewidths=0.5, length=5),
            o('grey', sst, range(-1,21), linewidths=[0.7, 1.2,] + [0.7, 0.7, 0.7, 0.7, 1.2]*4, alpha=0.5),
            o('yellow', ff10, [17.2, ], colors='gold'),
            o('orange', ff10, [24.5, ], colors='coral'),
            o('red', ff10, [32.7, ], colors='crimson'),
    ], name='Surface fluxes, 10m winds and SSTs'),
}

def _select(plot_names):
    return {plot_name: plot_archetypes[plot_name] for plot_name in plot_names}

plots = {
    'no': {
        'vestland': _select(['t2m_msl','t925_msl','t850_msl','q925_msl','q850_msl','w850_ff','w500_winds','w700_winds','ff10_caos','rh2m_tp','clba_msl','shf_winds']),
        'snorway': _select(['t2m_msl','t925_msl','t850_msl','q925_msl','q850_msl','w850_ff','w500_winds','w700_winds','ff10_caos','rh2m_tp','clba_msl','shf_winds']),
        'scandes': _select(['t2m_msl','t925_msl','t850_msl','q925_msl','q850_msl','w850_ff','w500_winds','w700_winds','ff10_caos','rh2m_tp','clba_msl','shf_winds']),
    },
    'ec_local': {
        'scandes': _select(['t2m_msl','t925_msl','t850_msl','q925_msl','q850_msl','ff10_caos','rh2m_tp','shf_winds']),
    },
}

del o

DECORATIONS = False
FILETYPE = 'png'
DATEFMT = '%Y%m%d%H'
STD_PLOTCONF = {
    'coastcolor': 'k',
    'coastwidth': 0.5,
    'grid_alpha': 0.25,
    'grid_linestyle': '-',
    'grid_latmax': 90,
    'show': False,
    'title': None,
}
STD_PLOTCONF_PER_FCSRC = {
    'no': dict(vector_disable_interpolation=True),
}

# Doing the actual plotting
class plotter(object):

    # Initalise and setup some metadata
    def __init__(self, domainname, domain, fcsrc, plotname, plotdef):
        self.plotname = plotname
        self.domainname = domainname
        self.fcsrc = fcsrc
        self.plotdef = plotdef

        self.requires = [(plotdef.shading.level, plotdef.shading.name), ] + [(o.var.level, o.var.name) for o in plotdef.overlays]
        self.std_plotconf = copy.copy(STD_PLOTCONF)
        self.std_plotconf.update(STD_PLOTCONF_PER_FCSRC.get(fcsrc, {}))

        # Domain-specific plot configuration
        self.std_plotconf['m'] = domain.proj
        self.std_plotconf.update(domain.plotconf)

        if DECORATIONS:
            self.std_plotconf['fig_size'] = domain.fig_size_deco
            self.std_plotconf['show_legend'] = True
            self.std_plotconf['cb_orientation'] = 'vertical'
            self.std_plotconf['cb_expand_fig_fraction'] = 0.12
            self.std_plotconf['cb_shrink'] = 0.65
            
        else:
            self.std_plotconf['fig_size'] = domain.fig_size
            self.std_plotconf['cb_disable'] = True
    
    # Do the art; to be overriden in derived classes
    def plot(self, data, static, dateinit, datevalid):
        self.std_plotconf['save'] = '%s/%s/%s/%s_for_%s.%s' % (
                self.domainname, self.plotname, self.fcsrc,
                dateinit.strftime(DATEFMT), datevalid.strftime(DATEFMT),
                FILETYPE
        )

        fi = plt.figure(figsize=self.std_plotconf['fig_size'], dpi=96)
        fi.subplotpars.update(left=0.001, right=0.999, top=0.999, bottom=0.001)
        
        data_available = True
        for qplev in self.requires:
            data_available &= qplev in data

        if not data_available:
            fi.text(0.5, 0.5, 'Error: Data unavailable', horizontalalignment='center', fontsize=24, bbox=dict(facecolor='red', alpha=0.5))
            plt.savefig(plotpath + '/' + self.std_plotconf['save'])

            return
        
        # Everything looks good, do the actual plot
        overlays = []
        for o in self.plotdef.overlays:
            plevq = (o.var.level, o.var.name)

            plotconf = copy.copy(self.std_plotconf)
            plotconf.update(o.plotconf)
            
            if o.otype == 'contour':
                overlays.append(
                    fig.map_overlay_contour(data[plevq], static, **pconfl.merge(*plevq, scale=o.contours, **plotconf))
                )
            elif o.otype == 'barbs':
                overlays.append(
                    fig.map_overlay_barbs(*data[plevq], static, **pconfl.merge(*plevq, **plotconf))
                )
            elif o.otype == 'shading':
                overlays.append(
                    fig.map_overlay_shading(data[plevq], static, **pconf.merge(*plevq, scale=o.contours, **plotconf))
                )
            else:
                raise ValueError(f'Unknown overlay type `{o.otype}`.')

        plevq = (self.plotdef.shading.level, self.plotdef.shading.name)
        plotconf = pconf.merge(*plevq, overlays=overlays, **self.plotdef.plotconf, **self.std_plotconf)
        fig.map(data[plevq], static, **plotconf)

        return


# Convert the human-readable level info into the normalised plev identifier
def level2plev(level):
    if level[-4:] == ' hPa':
        return level[:-4]
    elif level[-2:] == ' K':
        return 'pt'+level[:-2]
    elif level == 'PV 2':
        return 'pv2000'
    elif level == '':
        return 'sfc'
    else:
        raise ValueError(f'Unknown vertical level `{level}`.')



# C'est le fin
