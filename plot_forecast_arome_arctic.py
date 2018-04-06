#!/usr/bin/env python
# -*- encoding: utf-8

import copy

import matplotlib as mpl
mpl.use('Agg')

from dynlib.shorthands import *
from dynlib import utils
from settings.metno import *

from current_fc_arome import get_current_fc_arome


######################################################
# The base of _everything_

# Genering plot
class plotter(object):
	filetype = 'png'
	fcname = 'no_for_arctic'
	
	# Add colorbar and legend
	decorations = False

	# Which data is required for the plot
	requires=[]
	requires_diagnostic = []
	fmt = '%Y%m%d%H'

	std_plotconf = {
		'm': proj.AromeArcticMap,
		'coastcolor': 'k',
		'coastwidth': 0.5,
		'grid_alpha': 0.25,
		'grid_linestyle': '-',
		'grid_latmax': 90,
		'show': False,
		'title': None,
	}
	
	figsize = (5.0,6.375)
	figsize_deco = (5.68182,6.375)

	
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


######################################################
# Plot archetypes

# Temperature shading and MSLP contours
class t_msl(plotter):
	pass

# Total surface fluxes, and surface flux ratios: latent/total, sensible/total
class tshf(plotter):
	def cal_tshf(self, data, static):
		if not 'tshff' in data:
			data['tshff'] = data['LE'] + data['H']
		if not 'sshff_frac' in data:
			data['sshff_frac'] = data['H'] / data['tshff']
		if not 'slhf_frac' in data:
			data['slhff_frac'] = data['LE'] / data['tshff']

# Wind speed
class ff(plotter):
	def cal_ff(self, data, static):
		if not 'ff' in data:
			data['ff'] = np.sqrt(data['u']**2.0 + data['v']**2.0)

# 10m wind speed
class ff10(ff):
	def cal_ff10(self, data, static):
		if not 'ff_10m' in data:
			data['ff_10m'] = np.sqrt(data['x_wind_10m']**2.0 + data['y_wind_10m']**2.0)

# Precipitation
class precip(plotter):
	# Initial precip seems to be a fortran fail value that translates to an all-pink initial plot
	def zero_init_precip(self, data, static):
		if 'precipitation_amount' in data:
			data['precipitation_amount'][0,::] = 0.0



# Temperature@2m shading and MSLP contours
class t2m_msl(t_msl):
	requires = ['air_temperature_2m', 'air_pressure_at_sea_level']
	plotname = 't2m_msl'

	def plot(self, data, static, dateinit, datevalid):
		done = t_msl.plot(self, data, static, dateinit, datevalid)
		if done:
			return True

		overlays = [
			fig.map_overlay_contour(data['air_pressure_at_sea_level'], static, **conf.plot.merge('sfc', 'msl', 
				contour_labels=True, 
				contour_labels_format='%1.0f',
				contour_labels_scale=range(940,1060,10), 
				linewidths=[1], 
				scale=range(900,1070,2) ) ), 
			fig.map_overlay_contour(data['air_temperature_2m'], static, **conf.plot.merge('sfc', 't2m',
				linewidths=[1], 
				linestyles='dashed',
				scale=range(0,2,2) ) ),
		]
		plotconf = conf.plotf.merge('sfc', 't2m',
				overlays=overlays,
				cmap=cm.t, # Set a colormap
				scale=range(-34,36,2),
				ticks=range(-30,31,10),
				**self.std_plotconf
		)
		fig.map(data['air_temperature_2m'], static, **plotconf)

		return True


# Surface sensible and latent heat fluxes, near surface wind barbs, dangerous winds and MIZ.
class shf_winds(tshf, ff10):
	requires = ['H', 'LE', 'x_wind_10m', 'y_wind_10m', 'SIC', 'SST']
	requires_diagnostic = [tshf.cal_tshf, ff10.cal_ff10, ]
	plotname = 'shf_winds' 
	
	std_plotconf = ff10.std_plotconf
	std_plotconf['vector_disable_interpolation'] = True
	std_plotconf['vector_space_interval'] = 30

	def plot(self, data, static, dateinit, datevalid):
		done = plotter.plot(self, data, static, dateinit, datevalid)
		if done:
			return True

		shf = [-300,-200,-140,-100,-70,-50,-30,-20,-14,-10, 30,50,70,100,140,200,300,500,700,1000,]
		shft = [-10000,]+shf+[10000,]

		overlays = [
			fig.map_overlay_barbs(data['x_wind_10m'], data['y_wind_10m'], static, **conf.plot.merge('sfc', 'ff10', 
				linewidths=0.5,
				**self.std_plotconf) ),
			fig.map_overlay_contour(data['ff_10m'], static, **conf.plot.merge('sfc', 'ff10',
				colors='gold',
				linewidths=[1],
				scale=[17.2, ] ) ),
			fig.map_overlay_contour(data['ff_10m'], static, **conf.plot.merge('sfc', 'ff10',
				colors='coral',
				linewidths=[1.5],
				scale=[24.5, ] ) ),
			fig.map_overlay_contour(data['ff_10m'], static, **conf.plot.merge('sfc', 'ff10',
				colors='crimson',
				linewidths=[2],
				scale=[32.7, ] ) ),
			fig.map_overlay_contour(data['SIC'], static, **conf.plot.merge('sfc', 'sic',
				colors='blueviolet',
				linewidths=[1],
				scale=[0.2, 0.8] ) ),
			fig.map_overlay_contour(data['SST'], static, **conf.plot.merge('sfc', 'sst',
				colors='k',
				alpha=0.5,
				linewidths=[0.7],
				scale=[-1,1,2,3,4,6,7,8,9,11,12,13,14,16,17,18,19] ) ),
			fig.map_overlay_contour(data['SST'], static, **conf.plot.merge('sfc', 'sst',
				colors='k',
				alpha=0.6,
				linewidths=[1],
				scale=np.arange(0,21,5) ) ),
		]

		plotconf = conf.plotf.merge('sfc', 'tshff',
				cmap=cm.BrBG,
				scale=shf,
				norm=mpl.colors.BoundaryNorm(shft, 256),
				extend='both',
				cb_tickspacing='uniform',
				overlays=overlays,
				**self.std_plotconf
		)
		fig.map(data['tshff'], static, **plotconf)

		return True


# Near-surface relative humidity, total precipitation and MIZ
class rh2m_tp(precip):
	requires = ['relative_humidity_2m', 'precipitation_amount', 'SIC']
	requires_diagnostic = [precip.zero_init_precip, ]
	plotname = 'rh2m_tp'

	def plot(self, data, static, dateinit, datevalid):
		done = precip.plot(self, data, static, dateinit, datevalid)
		if done:
			return True

		s=[0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.4, 2.0, 3.0, 5.0, 7.0, 10.0] 
		st=[0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.4, 2.0, 3.0, 5.0, 7.0, 10.0, 1000.0] 
		overlays = [
			fig.map_overlay_shading(data['precipitation_amount'], static, **conf.plotf.merge('sfc', 'trr',
				cmap=cm.trr, # Set a colormap
				norm=mpl.colors.BoundaryNorm(st, 256),
				cb_tickspacing='uniform',
				extend='max',
				alpha=0.5,
				scale=s,
				ticks=st,
				**self.std_plotconf ) ), 
			fig.map_overlay_contour(data['SIC'], static, **conf.plot.merge('sfc', 'sic',
				colors='blueviolet',
				linewidths=[1],
				scale=[0.2, 0.8] ) ),
		]

		s=[0.2, 0.4, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.99] 
		st=[-1, 0.2, 0.4, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 0.99, 10.0] 
		plotconf = conf.plotf.merge('sfc', 'rh2m',
				cmap=cm.Greys_r, # Set a colormap
				norm=mpl.colors.BoundaryNorm(st, 256),
				#cb_tickspacing='uniform',
				extend='both',
				scale=s,
				ticks=st,
				overlays=overlays,
				**self.std_plotconf
		)
		plotconf['cb_disable'] = True
		fig.map(data['relative_humidity_2m'], static, **plotconf)

		return True


# -----------------------------------------------------------------------------

# Most recent available data
forecast = get_current_fc_arome()

# Override 
#forecast = dt(2018,1,24,12)
plot_only_init = False

print('Plotting the AROME Arctic %s forecasts' % forecast.strftime('%Y-%m-%d %H'))

plots = [
	shf_winds(),
	t2m_msl(), 
	rh2m_tp(),
]

fname = 'arome_arctic_pp_2_5km_%s' % forecast.strftime('%Y%m%dT%HZ')
fname2 = 'arome_arctic_sfx_2_5km_%s' % forecast.strftime('%Y%m%dT%HZ')
try:	
	#print('Looking for %s' % fname)
	f, static = metopen(fname)
	f2 = metopen(fname2, no_static=True)

	# We need to replace the auto-detected x dimension with the alternative lon dimension
	static.x = f.variables['longitude'][::]
	static.y = f.variables['latitude'][::]
	static.gridtype = 'latlon'
	#static.rebuild_grid()
except ValueError:	
	print('Warning: File %s not readable.' % fname)
	class Bunch(dict):
		def __init__(self,**kw):
			dict.__init__(self,kw)
			self.__dict__ = self
	f = Bunch(variables=[], close=lambda: None)
	
	t = range(0,67,3)
	static = Bunch(t=t, t_parsed=[forecast + i*td(0,3600) for i in t])


data = {}
for plot in plots:
	plot.error = False
	for q in plot.requires:
		if q not in f.variables:
			if q not in f2.variables:
				print('%s not available!' % q)
				plot.error = True
			else:
				data[q] = utils.scale(f2.variables[q])[...,10:-10,10:-10].squeeze()
				
		elif q not in data:
			data[q] = utils.scale(f.variables[q]).squeeze()
	
	if not plot.error:
		for fun in plot.requires_diagnostic:
			fun(plot, data, static)

f.close()
			

for tidx, date in zip(range(len(static.t)), static.t_parsed):
	# Plot only 3-hourly data to speed up plotting
	if not date.hour % 3 == 0:
		continue

	# Plot only initial time step
	if plot_only_init and not date == forecast:
		continue

	data_inst = {}
	for q in data:
		data_inst[q] = data[q][tidx]
	
	for plot in plots:
		plot.plot(data_inst, static, forecast, date)
		plt.close()


# the end
