#!/usr/bin/env python
# -*- encoding: utf-8


import copy
import matplotlib as mpl
import codecs
from datetime import datetime as dt, timedelta as td

from dynlib.shorthands import *
from settings.common2 import pconf, pconfl, WEB_ROOT, VAERKART_ROOT

from update_lehmkuhl_position import get_lehmkuhl_position

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
    _replace_colornames = {
        'tab:blue': 'steelblue',
    }

    def __init__(self, colorlabel, variable, contours, otype='contour', **plotconf):
        self.colorlabel = colorlabel
        if 'colors' in plotconf and type(plotconf['colors']) == str:
            self.colorclass = self._replace_colornames.get(plotconf['colors'], plotconf['colors'])
        else:
            self.colorclass = colorlabel
        self.plotconf = plotconf
        self.var = variable
        self.contours = contours
        self.otype = otype
        
        if 'scale_label' in plotconf:
            self.contour_label = plotconf['scale_label']
        elif type(contours) in (list, np.ndarray):
            self.contour_label = 'contours at ' + ', '.join(map(str, contours))
        elif type(contours) == range:
            self.contour_label = f'contour interval = {contours.step}'
        elif type(contours) == type(None):
            self.contour_label = None
        else:
            raise ValueError(f'Unknown type of contour specification, `{type(contours)}`.')

# Defining data sources
datasources = ['no', 'ecmwf', 'noaa', 'no_kyst', ]

# Defining domains

# Parameterised plot domain following Statsraad Lehmkuhl
def lehmkuhl_proj_factory(lat, lon):
    # dynlib requires the map projection to be a callable returning the projection object. 
    # With this construction the lat/lon variables are bound to the lambda statement at the 
    # time of definition of this class and function, rather than at the time of execution 
    # of the lambda construct (where they would otherwise no longer be available as local/
    # global variables).
    return lambda: proj.Basemap(projection='gnom', width=6000000, height=6000000,
        lat_0=lat, lon_0=lon, resolution='l')

llat, llon = get_lehmkuhl_position()
domains = {
    'npolar': domain(proj.n_hemisphere_forecast, (6.4,6.4), (7.27273,6.4), vector_space_numbers_xy=(45, 45), quiver_width=0.002),
    'spolar': domain(proj.s_hemisphere_forecast, (6.4,6.4), (7.27273,6.4), vector_space_numbers_xy=(45, 45), quiver_width=0.002),
    'natl': domain(proj.N_Atlantic_forecast, (7.2,4.8), (8.18182,4.8), vector_space_numbers_xy=(45, 30), quiver_width=0.002),
    'lehmkuhl': domain(lehmkuhl_proj_factory(llat, llon), (6.4,6.4), (7.27273,6.4), vector_space_numbers_xy=(45, 45), quiver_width=0.002, mark=(llon, llat), mark_kwargs=dict(markersize=20, markeredgewidth=1.5)),
    'tindpac': domain(proj.Tropical_IndoPacific, (12.5,5.0), (14.2,5.0), vector_space_numbers_xy=(110, 44), quiver_width=0.001),
    'scandes': domain(proj.Scandinavia, (5.5,6.18), (6.25,6.18), vector_space_interval=30, vector_space_numbers_xy=(30, 40)),
    'snorway': domain(proj.S_Norway, (6.4,6.4), (7.27273,6.4), vector_space_interval=10),
    'vestland': domain(proj.Vestland, (6.4,6.4), (7.27273,6.4), vector_space_interval=5),
    'barents': domain(proj.Barents_Sea, (5.0,6.375), (5.68182,6.375), vector_space_interval=30, vector_space_numbers_xy=(30,40)),
}

# Defining variables
variables = {
    'z500': variable('Geopotential', 'gpdm', '500 hPa'),
    't850': variable('Temperature', '°C', '850 hPa'),
    't925': variable('Temperature', '°C', '925 hPa'),
    'q850': variable('Specific humidity', 'g/kg', '850 hPa'),
    'q925': variable('Specific humidity', 'g/kg', '925 hPa'),
    'eqpt850': variable('Equivalent potential temperature', 'K', '850 hPa'),
    'def850': variable('Deformation', '10⁻⁵/s', '850 hPa'),
    't2': variable('2m Temperature', '°C', ''),
    'rh2': variable('2m Relative humidity', '%', ''),
    'ff10': variable('10m Wind speed', 'm/s', ''),
    'fg10': variable('10m Wind gusts', 'm/s', ''),
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

    't850p': variable('Temperature percentiles', '', '850 hPa', 'based on ERA-5 1979-2020'),
    't850a': variable('Temperature anomaly', 'K', '850 hPa', 'based on ERA-5 1979-2020'),

    'msl': variable('Sea-level pressure', 'hPa', ''),
    'mslc': variable('Ensemble ctrl sea level pressure', 'hPa', ''),
    'mslm': variable('Ensemble mean sea level pressure', 'hPa', ''),
    'cp': variable('Convective precipitation', 'mm/h', ''),
    'lsp': variable('Large-scale precipitation', 'mm/h', ''),
    'cape': variable('Convective available potential energy', 'J/kg', ''),
    'tp': variable('Total precipitation', 'mm/h', ''),
    'sic': variable('Sea ice concentration', '', ''),
    'sst': variable('Sea-surface temperature', '°C', ''),
    'cycfreq': variable('Cyclone occurrence', '%', ''),
    'jetfreq': variable('Jet occurrence within 300 km', '%', 'PV 2'),
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
    'ffpv2': variable('Wind speed filtered to T84', 'm/s', 'PV 2'),
    'defang850': variable('Axes of dilatation', '', '850 hPa'),
    'iwvt': variable('Column integral water vapour transport vector', 'kg m/s', ''),
    'absiwvt': variable('Column integral water vapour transport', 'kg m/s', ''),
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

cc_scale = np.array([0,] + list(np.arange(0.0625,0.95,0.125)) + [1,])
cc_ticks = (cc_scale[1:]+cc_scale[:-1])/2.0
cc_ticklabels = ["0/8","1/8", "2/8", "3/8", "4/8", "5/8", "6/8", "7/8", "8/8"]

t_ano_scale = [-30,-25,-21,-18,-15,-13,-11,-9,-7,-5,-3,-1,1,3,5,7,9,11,13,15,18,21,25,30] 

pv_scale = np.arange(1.0,9.1,1.0)

freq_scale = np.arange(0,1.01,0.05)
freq_ticks = np.arange(0,1.01,0.2)
freq_ticklabels = range(0,101,20)

# Defining what is available per plot domain and data source
def plot_archetypes(msl_ci=2, msl_reduce=False, sst_reduce=False, tcwv_extratropic=False, sh=False):
    if msl_reduce:
        selected_msl_kwargs = dict(alpha=0.8, linewidths=[0.5])
    else:
        selected_msl_kwargs = dict(contour_labels=True, contour_labels_format='%1.0f')

    if tcwv_extratropic:
        tcwv_scale = range(4,51,2)
        tcwv_ticks = range(10,51,10)
    else:
        tcwv_scale = range(4,65,2)
        tcwv_ticks = range(10,61,10)

    if sst_reduce:
        sst_scale = [-1,] + list(range(0,31,2))
    else:
        sst_scale = range(-1,21)

    if sh:
        pv_ticklabels = np.arange(-1.0,-9.1,-1.0)
    else:
        pv_ticklabels = np.arange(1.0,9.1,1.0)

    return {
    'z500_msl': plot(z500, scale=range(476,604,4), ticks=range(480,601,20), overlays=[
            o('white', z500, [552,], colors='white', linewidths=[2]), 
            o('black', msl, range(900,1070,msl_ci), contour_labels=True, contour_labels_format='%1.0f'),
        ], name='500 hPa Geopotential and SLP'), 
    'tcwv': plot(tcwv, scale=tcwv_scale, ticks=tcwv_ticks, overlays=[
            o('black arrows', iwvt, None, otype='quiver', alpha=0.7), 
            o('magenta', lsp, [1,3,10], colors='orchid', linewidths=[1.65]),
            o('cyan', cp, [1,3,10], colors='c', linewidths=[1.65]),
            o('dark red', t850, [-5,], colors='firebrick', linestyles='solid'),
        ], name='Total column water vapour, fluxes and precip.'),
    'iwvt_axis': plot(absiwvt, scale=np.arange(50,951,50), ticks=np.arange(200,951,200), overlays=[
            o('yellow', iwvtaxes, None, otype='lines', linewidths=(4,2), linecolors=('w','gold')),
            o('magenta', lsp, [1,3,10], colors='orchid', linewidths=[1.65]),
            o('cyan', cp, [1,3,10], colors='c', linewidths=[1.65]),
            o('dark red', t850, [-5,], colors='firebrick', linestyles='solid'),
        ], name='Water vapour transport, axes, and precipitation'),
    'tcc': plot(lcc, scale=cc_scale, ticks=cc_ticks, ticklabels=cc_ticklabels, extend='neither', coastcolor='0.7', markercolor='0.7', overlays=[
            o('orange shading', mcc, cc_scale, otype='shading', extend='neither', antialiased=True, cb_disable=True, alpha=0.5),
            o('white shading', hcc, cc_scale, otype='shading', extend='neither', antialiased=True, cb_disable=True, alpha=0.4),
        ], name='Cloud cover'),
    'cycfreq_msl': plot(cycfreq, scale=freq_scale, ticks=freq_ticks, ticklabels=freq_ticklabels, overlays=[
            o('black', mslc, range(900,1070,msl_ci), linewidths=[0.5,], alpha=0.4),
            o('orange', mslm, range(900,1070,msl_ci), linewidths=[0.5,], alpha=0.7, colors='tab:orange'),
        ], name='Ensemble cyclone detections'),
    'jetfreq_msl': plot(jetfreq, scale=freq_scale, ticks=freq_ticks, ticklabels=freq_ticklabels, overlays=[
            o('black', mslc, range(900,1070,msl_ci), linewidths=[0.5,], alpha=0.4),
            o('orange', mslm, range(900,1070,msl_ci), linewidths=[0.5,], alpha=0.7, colors='tab:orange'),
        ], name='Ensemble jet detections'),
    'ptpv2_jets': plot(ptpv2, scale=np.arange(270,396,5), ticks=[270,285,300,315,330,350,370,395], overlays=[
            o('black', ffpv2, [30, 45, 60, 75, 90], linewidths=[2,]),
            o('white', jetaxespv2, None, otype='lines', linewidths=(6,4), linecolors=('k','w')),
        ], name='PV2 Pot. temperature, jets and wind speed'),
    'pvpt315_irot_wind': plot(pvpt315, scale=pv_scale, ticks=pv_scale, ticklabels=pv_ticklabels, overlays=[
            o('black', pvpt315, [2, ], linewidths=[1.5,]),
            o('black', irbarbspt315, None, otype='quiver'),
        ], name='315 K Pot. Vorticity and irrot. winds'),
    'pvpt330_irot_wind': plot(pvpt330, scale=pv_scale, ticks=pv_scale, ticklabels=pv_ticklabels, overlays=[
            o('black', pvpt330, [2, ], linewidths=[1.5,]),
            o('black', irbarbspt330, None, otype='quiver'),
        ], name='330 K Pot. Vorticity and irrot. winds'),
    't2m_msl': plot(t2, scale=range(-34,36,2), ticks=range(-30,31,10), overlays=[
            o('black dashes', t2, [0,], linestyles='dashed'),
            o('black', msl, range(900,1070,msl_ci), contour_labels=True, contour_labels_format='%1.0f'),
        ], name='2m Temperature and SLP'),
    't925_msl': plot(t925, scale=range(-34,36,2), ticks=range(-30,31,10), overlays=[
            o('black dashes', t925, [0,], linestyles='dashed'),
            o('black', msl, range(900,1070,msl_ci), contour_labels=True, contour_labels_format='%1.0f'),
            o('black', barbs925, None, otype='barbs', alpha=0.5, linewidths=0.5, length=5),
        ], name='925 hPa Temperature, SLP and wind barbs'),
    't850_msl': plot(t850, scale=range(-34,36,2), ticks=range(-30,31,10), overlays=[
            o('black dashes', t850, [0,], linestyles='dashed'),
            o('black', msl, range(900,1070,msl_ci), **selected_msl_kwargs),
            o('black', barbs850, None, otype='barbs', alpha=0.5, linewidths=0.5, length=5),
        ], name='850 hPa Temperature, SLP and wind barbs'),
    't850_perc': plot(t850a, scale=t_ano_scale, norm=mpl.colors.BoundaryNorm([-np.inf,]+t_ano_scale+[np.inf,], 256), cb_tickspacing='uniform', overlays=[
            o('black', t850p, [3.5, 15.5], scale_label='contours at monthly recurrence'),
            o('grey', t850p, [1.5, 17.5], scale_label='contours at yearly recurrence', colors='0.3'),
            o('white', t850p, [0.5, 18.5], scale_label='contours where new record', colors='w'),
        ], name='850 hPa Temperature anomalies'),
    'q925_msl': plot(q925, scale=np.arange(1,12.1,0.5), ticks=np.arange(2,12.1,2), overlays=[
            o('dark red', t850, [-5,], colors='firebrick', linestyles='solid'),
            o('black', msl, range(900,1070,msl_ci), contour_labels=True, contour_labels_format='%1.0f'),
            o('black', barbs925, None, otype='barbs', alpha=0.5, linewidths=0.5, length=5),
    ], name='925 hPa Specific humidity, SLP and wind barbs'),
    'q850_msl': plot(q850, scale=np.arange(1,12.1,0.5), ticks=np.arange(2,12.1,2), overlays=[
            o('dark red', t850, [-5,], colors='firebrick', linestyles='solid'),
            o('black', msl, range(900,1070,msl_ci), contour_labels=True, contour_labels_format='%1.0f'),
            o('black', barbs850, None, otype='barbs', alpha=0.5, linewidths=0.5, length=5),
    ], name='850 hPa Specific humidity, SLP and wind barbs'),
    'eqpt850_cape': plot(eqpt850, scale=range(250,351,4), ticks=range(260,341,20), overlays=[
            o('blue shading', frovo850, [0.5, 2], otype='shading', cmap=None, colors=['cornflowerblue',], extend='neither', antialiased=True, cb_disable=True, alpha=0.7),
            o('light green', cape, [250, ], linewidths=[0.7, ], colors='palegreen', alpha=0.7),
            o('yellow', cape, [500, ], linewidths=[0.7, ], colors='gold'),
            o('orange', cape, [1000, ], linewidths=[0.7, ], colors='coral'),
            o('red', cape, [2000, ], linewidths=[0.7, ], colors='crimson'),
            o('black', msl, range(900,1070,msl_ci), **selected_msl_kwargs),
        ], name='850 hPa EQPT, CAPE and fronts'),
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
    #'ff10_caos': plot(ff10, scale=np.arange(5.0,32.6,2.5), overlays=[
    #        o('blue', caoidx, [2, 4, 8, 12,], linewidths=[0.9, 1.5, 1.2, 1.2, ], colors='darkblue'),
    #        o('black', barbs10, None, otype='barbs', alpha=0.5, linewidths=0.5, length=5),
    #], name='10m wind speed, barbs and CAO index'),
    'ff10_gusts': plot(ff10, scale=np.arange(5.0,32.6,2.5), overlays=[
            o('dark blue', fg10, [17.2, ], linewidths=[0.7, ], colors='darkblue'),
            o('orange', fg10, [24.5, ], colors='coral'),
            o('red', fg10, [32.7, ], colors='crimson'),
            o('black', barbs10, None, otype='barbs', alpha=0.5, linewidths=0.5, length=5),
    ], name='10m wind speed, barbs and gusts'),
    'rh2m_tp': plot(rh2, scale=rh_scale, cmap='Greys_r', ticks=rh_ticks, norm=mpl.colors.BoundaryNorm(rh_ticks, 256), overlays=[
            o('blue shading', tp, tp_scale, otype='shading', alpha=0.5, ticks=tp_ticks, extend='max', ticklabels=tp_labels,
                cb_tickspacing='uniform', norm=mpl.colors.BoundaryNorm(tp_ticks, 256)),
            o('violet', sic, [0.2, 0.8], colors='blueviolet'),
            o('dark red', t850, [-5,], colors='firebrick', linestyles='solid'),
    ], name='2m Relative humidity and precipitation'),
    'clba_msl': plot(clba, scale=clba_scale[:-1], ticks=clba_ticks, cmap='cividis', norm=mpl.colors.BoundaryNorm(clba_scale, 256),
        cb_tickspacing='uniform', extend='max', overlays=[
            o('black', msl, range(900,1070,msl_ci), contour_labels=True, contour_labels_format='%1.0f'),
    ], name='Cloud base altitude and SLP'),
    'cao_winds': plot(caoidx, scale=range(1,16), ticks=range(4,16,4), cmap='afmhot_r', overlays=[
            o('black', barbs10, None, otype='barbs', alpha=0.5, linewidths=0.5, length=5),
            o('grey', sst, sst_scale, linewidths=[0.7, 1.2,] + [0.7, 0.7, 0.7, 0.7, 1.2]*4, alpha=0.5),
            o('violet', sic, [0.2, 0.8], colors='blueviolet'),
    ], name='Cold-air outbreak index, 10m winds, SSTs and MIZ'),
    'shf_winds': plot(sthff, scale=shf_scale, cmap='BrBG', norm=mpl.colors.BoundaryNorm(shf_ticks, 256),
        cb_tickspacing='uniform', overlays=[
            o('black', barbs10, None, otype='barbs', alpha=0.5, linewidths=0.5, length=5),
            o('grey', sst, sst_scale, linewidths=[0.7, 1.2,] + [0.7, 0.7, 0.7, 0.7, 1.2]*4, alpha=0.5),
            o('violet', sic, [0.2, 0.8], colors='blueviolet'),
            o('yellow', ff10, [17.2, ], colors='gold'),
            o('orange', ff10, [24.5, ], colors='coral'),
            o('red', ff10, [32.7, ], colors='crimson'),
    ], name='Surface fluxes, 10m winds, SSTs and MIZ'),
    'sshf_winds': plot(sshff, scale=shf_scale, cmap='BrBG', norm=mpl.colors.BoundaryNorm(shf_ticks, 256),
        cb_tickspacing='uniform', overlays=[
            o('black', barbs10, None, otype='barbs', alpha=0.5, linewidths=0.5, length=5),
            o('grey', sst, sst_scale, linewidths=[0.7, 1.2,] + [0.7, 0.7, 0.7, 0.7, 1.2]*4, alpha=0.5),
            o('violet', sic, [0.2, 0.8], colors='blueviolet'),
            o('yellow', ff10, [17.2, ], colors='gold'),
            o('orange', ff10, [24.5, ], colors='coral'),
            o('red', ff10, [32.7, ], colors='crimson'),
    ], name='Sensible heat flux, 10m winds, SSTs and MIZ'),
    'slhf_winds': plot(slhff, scale=shf_scale, cmap='BrBG', norm=mpl.colors.BoundaryNorm(shf_ticks, 256),
        cb_tickspacing='uniform', overlays=[
            o('black', barbs10, None, otype='barbs', alpha=0.5, linewidths=0.5, length=5),
            o('grey', sst, sst_scale, linewidths=[0.7, 1.2,] + [0.7, 0.7, 0.7, 0.7, 1.2]*4, alpha=0.5),
            o('violet', sic, [0.2, 0.8], colors='blueviolet'),
            o('yellow', ff10, [17.2, ], colors='gold'),
            o('orange', ff10, [24.5, ], colors='coral'),
            o('red', ff10, [32.7, ], colors='crimson'),
    ], name='Latent heat flux, 10m winds, SSTs and MIZ'),
}

## Old ECMWF plot definitions
#old_ecmwf_plots = [
#    plot('deform850_fronts', def850, [o('black double-arrows', defang850, None), o('dark cyan shading', frovo850, None), 
#        o('dark cyan contour', tp, [1,5]), o('red, blue, purple', fronts850, None), o('dark red', t850, [-5,]), ],
#        name='850 hPa Deformation, fronts and precipitation'),
#]

def _select(plot_names, **kwargs):
    plots = plot_archetypes(**kwargs)
    return {plot_name: plots[plot_name] for plot_name in plot_names}

plots = {
    'no': {
        'vestland': _select(['t2m_msl','t925_msl','t850_msl','q925_msl','q850_msl','w850_ff','w500_winds','w700_winds','ff10_gusts','rh2m_tp','clba_msl','cao_winds','shf_winds']),
        'snorway': _select(['t2m_msl','t925_msl','t850_msl','q925_msl','q850_msl','w850_ff','w500_winds','w700_winds','ff10_gusts','rh2m_tp','clba_msl','cao_winds','shf_winds']),
        'scandes': _select(['t2m_msl','t925_msl','t850_msl','q925_msl','q850_msl','w850_ff','w500_winds','w700_winds','ff10_gusts','rh2m_tp','clba_msl','cao_winds','shf_winds']),
    },
    'no_arctic': {
        'barents': _select(['t2m_msl','t925_msl','t850_msl','q925_msl','q850_msl','w850_ff','w500_winds','w700_winds','ff10_gusts','rh2m_tp','clba_msl','cao_winds','shf_winds']),
    },
    'ec_local': {
        'scandes': _select(['t2m_msl','t925_msl','t850_msl','q925_msl','q850_msl','ff10_gusts','rh2m_tp','cao_winds','shf_winds']),
        'barents': _select(['t2m_msl','t925_msl','t850_msl','q925_msl','q850_msl','ff10_gusts','rh2m_tp','cao_winds','shf_winds']),
    },
    'ec': {
        'natl': _select(['z500_msl', 't850_msl', 't850_perc', 'eqpt850_cape', 'tcwv', 'iwvt_axis', 'tcc', 'sshf_winds', 'slhf_winds', 'cao_winds',
                'cycfreq_msl', 'jetfreq_msl', 'pvpt315_irot_wind', 'pvpt330_irot_wind', 'ptpv2_jets', ],
            msl_ci=5, msl_reduce=True, tcwv_extratropic=True, sst_reduce=True),
        'npolar':  _select(['z500_msl', 't850_msl', 'tcwv', 'cycfreq_msl', 'jetfreq_msl', 'pvpt315_irot_wind', 'pvpt330_irot_wind', 'ptpv2_jets', ],
            msl_ci=5, msl_reduce=True, sst_reduce=True),
        'spolar':  _select(['z500_msl', 't850_msl', 'tcwv', 'cycfreq_msl', 'jetfreq_msl', 'pvpt315_irot_wind', 'pvpt330_irot_wind', 'ptpv2_jets', ],
            msl_ci=5, msl_reduce=True, sst_reduce=True, sh=True),
        'lehmkuhl': _select(['t850_msl', 'eqpt850_cape', 'tcwv', 'ff10_gusts', 'tcc', 'rh2m_tp', ], msl_ci=5, msl_reduce=True, sst_reduce=True),
        'tindpac': _select(['t850_msl', 'eqpt850_cape', 'tcwv', 'rh2m_tp', ], msl_ci=5, msl_reduce=True, sst_reduce=True),
    },
    'noaa': {
        'natl': _select(['z500_msl', 't850_msl', 't850_perc', 'eqpt850_cape', 'tcwv', 'iwvt_axis', 'tcc', 'sshf_winds', 'slhf_winds', 'cao_winds', 'ptpv2_jets', ],
            msl_ci=5, msl_reduce=True, tcwv_extratropic=True, sst_reduce=True),
        'npolar':  _select(['z500_msl', 't850_msl', 'tcwv', 'ptpv2_jets', ],
            msl_ci=5, msl_reduce=True, sst_reduce=True),
        'spolar':  _select(['z500_msl', 't850_msl', 'tcwv', 'ptpv2_jets', ],
            msl_ci=5, msl_reduce=True, sst_reduce=True, sh=True),
    },
}

# (How) Can this be derived from the plot defintions above?
pages = {
    ('noaa', 'natl'): ('GFS forecasts North Atlantic', '/vaerkart.html'),
    ('noaa', 'npolar'): ('GFS forecasts Northern Hemisphere', '/vaerkart_npolar.html'),
    ('noaa', 'spolar'): ('GFS forecasts Southern Hemisphere', '/vaerkart_spolar.html'),
    ('ec', 'natl'): ('ECMWF forecasts North Atlantic (restricted)', '/closed/vaerkart_ec.html'),
    ('ec', 'npolar'): ('ECMWF forecasts Northern Hemisphere (restricted)', '/closed/vaerkart_ec_npolar.html'),
    ('ec', 'spolar'): ('ECMWF forecasts Southern Hemisphere (restricted)', '/closed/vaerkart_ec_spolar.html'),
    ('ec', 'tindpac'): ('ECMWF forecasts Tropical Indopacific (restricted)', '/closed/vaerkart_ec_tindpac.html'),
    ('ec', 'lehmkuhl'): ('ECMWF forecasts Statsraad Lehmkuhl (restricted)', '/closed/vaerkart_ec_lehmkuhl.html'),
    ('ec', 'scandes'): ('ECMWF forecasts Scandinavia (restricted)', '/closed/vaerkart_ec_scandes.html'),
    ('ec', 'barents'): ('ECMWF forecasts Barents Sea (restricted)', '/closed/vaerkart_ec_barents.html'),
    ('ec', 'meteograms'): ('ECMWF forecast Meteograms (restricted)', '/closed/vaerkart_ec_meteograms.html'),
    ('no', 'vestland'): ('AROME forecasts Vestland', '/vaerkart_arome_vestland.html'),
    ('no', 'snorway'): ('AROME forecasts Southern Norway', '/vaerkart_arome.html'),
    ('no', 'scandes'): ('AROME forecasts Scandinavia', '/vaerkart_arome_scandes.html'),
    ('no', 'we60'): ('AROME forecasts Cross section 60°N', '/vaerkart_arome_we60.html'),
    ('no', 'barents'): ('AROME Arctic forecasts Barents Sea', '/vaerkart_arome_arctic.html'),
}

plots_per_page = {
    ('noaa', 'natl'): [],
    ('noaa', 'npolar'): [],
    ('noaa', 'spolar'): [],
    ('ec', 'natl'): plots['ec']['natl'],
    ('ec', 'npolar'): plots['ec']['npolar'],
    ('ec', 'spolar'): plots['ec']['spolar'],
    ('ec', 'lehmkuhl'): plots['ec']['lehmkuhl'],
    ('ec', 'tindpac'): plots['ec']['tindpac'],
    ('ec', 'scandes'): plots['ec_local']['scandes'],
    ('ec', 'barents'): plots['ec_local']['barents'],
    ('ec', 'meteograms'): [],
    ('no', 'vestland'): plots['no']['vestland'],
    ('no', 'snorway'): plots['no']['snorway'],
    ('no', 'scandes'): plots['no']['scandes'],
    ('no', 'we60'): [],
    ('no', 'barents'): plots['no_arctic']['barents'],
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
            elif o.otype == 'quiver':
                overlays.append(
                    fig.map_overlay_quiver(*data[plevq], static, **pconfl.merge(*plevq, **plotconf))
                )
            elif o.otype == 'shading':
                overlays.append(
                    fig.map_overlay_shading(data[plevq], static, **pconf.merge(*plevq, scale=o.contours, **plotconf))
                )
            elif o.otype == 'lines':
                for linewidth, linecolor in zip(plotconf['linewidths'], plotconf['linecolors']):
                    overlays.append(fig.map_overlay_lines(*data[plevq], static, linewidth=linewidth, linecolor=linecolor) )
            else:
                raise ValueError(f'Unknown overlay type `{o.otype}`.')

        plevq = (self.plotdef.shading.level, self.plotdef.shading.name)
        plotconf = pconf.merge(*plevq, overlays=overlays, **self.std_plotconf)
        plotconf.update(self.plotdef.plotconf) # plotdef.plotconf takes precedence over stuff defined in pconf, self.std_plotconf
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



def render_webpage(domain, fcsrc, date_fc, fclist, leadlist, leadlist_link):
    from jinja2 import FileSystemLoader, Environment
    env = Environment(loader=FileSystemLoader(searchpath=VAERKART_ROOT+'/web'))
    
    # Find saveto and plotlist by domain and fcsrc
    saveto = WEB_ROOT + pages[fcsrc,domain][1]
    plotlist = []
    for prefix, plot in plots_per_page[fcsrc,domain].items():
        plot.prefix = prefix
        plotlist.append(plot)

    # Rendering
    t = env.get_template('template_jinja2.html')
    c = {
        'plot_domains': pages.values(),
        'plot_domain': pages[fcsrc,domain][0],
        'fcsrc': fcsrc,
        'domain': domain,
        'plotlist': plotlist,
        'timlist': [date_fc + td(0,3600*lead) for lead in leadlist],
        'leadlist': leadlist,
        'leadlist_link': leadlist_link,
        'fclist': fclist,
        'initplot': plotlist[0],
        'date_begin': date_fc,
        'date_init': date_fc,
        'plotdir': 'maps',
        'display_details': False,
    }
    if fcsrc == 'ec':
        if domain == 'natl':
            c['archive'] = {
                'start': dt(2017,9,22),
                'plots': ['z500_msl', 't850_msl', 'tcwv', 'iwvt_axis', 'ptpv2_jets', ],
                'step': 12,
            }
        elif domain == 'npolar':
            c['archive'] = {
                'start': dt(2021,6,2),
                'plots': ['z500_msl', 't850_msl', 'tcwv', 'ptpv2_jets', ],
                'step': 12,
            }


    f = codecs.open(saveto, mode='w', encoding='utf-8')
    f.write(t.render(**c))
    f.close()

    return


# C'est le fin
