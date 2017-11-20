#!/usr/bin/env python
# -*- encoding: utf-8

import copy

import matplotlib as mpl
mpl.use('Agg')

from dynlib.shorthands import *
from settings.metno import *


######################################################
# The base of _everything_

# Genering plot
class plotter(object):
	filetype = 'png'
	fcname = 'no_for'
	
	# Add colorbar and legend
	decorations = False

	# Which data is required for the plot
	requires=[]
	requires_diagnostic = []
	fmt = '%Y%m%d%H'

	std_plotconf = {
		'm': proj.SNorwaymap,
		'coastcolor': 'gray',
		'coast_alpha': 0.5,
		'grid_alpha': 0.25,
		'grid_linestyle': '-',
		'grid_latmax': 90,
		'show': False,
		'title': None,
	}
	
	figsize = (6.4,6.4)
	figsize_deco = (7.1111,6.4)
	
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


class scandies(plotter):
	fcname = plotter.fcname + '_full'

	std_plotconf = copy.copy(plotter.std_plotconf)
	std_plotconf['m'] = proj.Scandimap

	figsize = (5.0,6.375)
	figsize_deco = (5.5556,6.375)


######################################################
# Plot archetypes

# Temperature shading and MSLP contours
class t_msl(plotter):
	pass

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
			fig.map_overlay_contour(data['air_pressure_at_sea_level'][0,::], static, **conf.plot.merge('sfc', 'msl', 
				contour_labels=True, 
				contour_labels_format='%1.0f',
				contour_labels_scale=range(940,1060,10), 
				linewidths=[1], 
				scale=range(900,1070,2) ) ), 
			fig.map_overlay_contour(data['air_temperature_2m'][0,::], static, **conf.plot.merge('sfc', 't2m',
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
		fig.map(data['air_temperature_2m'][0,::], static, **plotconf)

		return True


class t2m_msl_scandies(t2m_msl,scandies):
	requires = ['air_temperature_2m', 'air_pressure_at_sea_level']
	plotname = 't2m_msl'


# Near surface winds.
class ff10_wind(ff10):
	requires = ['x_wind_10m', 'y_wind_10m']
	requires_diagnostic = [ff10.cal_ff10, ]
	plotname = 'ff10_wind' 
	
	std_plotconf = ff10.std_plotconf
	std_plotconf['vector_disable_interpolation'] = True
	std_plotconf['vector_space_interval'] = 10

	def plot(self, data, static, dateinit, datevalid):
		done = plotter.plot(self, data, static, dateinit, datevalid)
		if done:
			return True

		overlays = [
			fig.map_overlay_barbs(data['x_wind_10m'], data['y_wind_10m'], static, **conf.plot.merge('sfc', 'ff10', **self.std_plotconf) ),
		]
		
		s = np.arange(5.0,32.6,2.5)
		plotconf = conf.plotf.merge('sfc', 'ff10',
				cmap=cm.ff, 
				scale=s,
				extend='both',
				overlays=overlays,
				**self.std_plotconf
		)
		fig.map(data['ff_10m'], static, **plotconf)

		return True


class ff10_wind_scandies(ff10_wind,scandies):
	requires = ['x_wind_10m', 'y_wind_10m']
	requires_diagnostic = [ff10.cal_ff10, ]
	plotname = 'ff10_wind' 

	std_plotconf = scandies.std_plotconf
	std_plotconf['vector_disable_interpolation'] = True
	std_plotconf['vector_space_interval'] = 30
	std_plotconf['cb_shrink'] = 0.65


# Total precipitation
class tp(precip):
	requires = ['precipitation_amount']
	requires_diagnostic = [precip.zero_init_precip, ]
	plotname = 'tp'

	def plot(self, data, static, dateinit, datevalid):
		done = precip.plot(self, data, static, dateinit, datevalid)
		if done:
			return True

		s=[0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.4, 2.0, 3.0, 5.0, 7.0, 10.0] 
		st=[0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.4, 2.0, 3.0, 5.0, 7.0, 10.0, 1000.0] 
		plotconf = conf.plotf.merge('sfc', 'trr',
				cmap=cm.trr, # Set a colormap
				norm=mpl.colors.BoundaryNorm(st, 256),
				cb_tickspacing='uniform',
				extend='max',
				scale=s,
				ticks=s,
				**self.std_plotconf
		)
		fig.map(data['precipitation_amount'], static, **plotconf)

		return True


class tp_scandies(tp,scandies):
	requires = ['precipitation_amount']
	requires_diagnostic = [precip.zero_init_precip, ]
	plotname = 'tp'


# -----------------------------------------------------------------------------

# Most recent available data
now = dt.now()
if now.hour in range(5,11):
	forecast = dt(now.year,now.month,now.day,0)
elif now.hour in range(11,17):
	forecast = dt(now.year,now.month,now.day,6)
elif now.hour in range(17,23):
	forecast = dt(now.year,now.month,now.day,12)
else:
	forecast = dt(now.year,now.month,now.day,18)
	if now.hour < 5:
		forecast -= td(1,0)

# Override 
#forecast = dt(2015,7,15,6)
plot_only_init = False

print 'Plotting the AROME %s forecasts' % forecast.strftime('%Y-%m-%d %H')

plots = [
	ff10_wind(), t2m_msl(), tp(), 
	ff10_wind_scandies(), t2m_msl_scandies(), tp_scandies(), 
]

fname = 'meps_det_pp_2_5km_%s' % forecast.strftime('%Y%m%dT%HZ')
try:	
	#print('Looking for %s' % fname)
	f, static = metopen(fname)

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
			print '%s not available!' % q 
			plot.error = True
		elif q not in data:
			data[q] = f.variables[q][::]
	
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
