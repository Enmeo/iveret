#!/usr/bin/env python
# -*- encoding: utf-8

import copy

import matplotlib as mpl
mpl.use('Agg')

import dynlib
import dynlib.detect
import dynlib.diag
import dynlib.sphere
import dynlib.thermodyn
import dynlib.utils

from dynlib.shorthands import *
from settings.ecmwf import *


conf.file_std = '%(time)d/ec.for-hr.%(time)d.%(plev)s.%(q)s'
conf.plotf[None,'sst','hook'] = sst_mask_offset_hr
conf.plot[None,'sst','hook'] = sst_mask_offset_hr

######################################################
# The base of _everything_

# Genering plot
class plotter(object):
	filetype = 'png'
	fcname = 'ec_for_scandies'
	
	# Add colorbar and legend
	decorations = False

	# Which data is required for the plot
	requires=[]
	requires_diagnostic = []
	fmt = '%Y%m%d%H'

	std_plotconf = {
		'm': proj.Scandimap,
		'coastcolor': 'gray',
		'coast_alpha': 0.5,
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

# 10m wind speed
class ff10(plotter):
	def cal_ff10(self, data, plev, static):
		if not ('ff10', plev) in data:
			data['ff10',plev] = np.sqrt(data['u10',plev]**2.0 + data['v10',plev]**2.0)

class rh2m(plotter):
	def rh2m_from_d2m(self, data, plev, static):
		if not ('rh2m', plev) in data:
			e = dynlib.thermodyn.e_sat_liq(data['d2m',plev])
			data['rh2m',plev] = dynlib.thermodyn.rh_from_e(e, data['t2m',plev])


######################################################
# Specific plots

class t2m_msl(plotter):
	requires = [('t2m', 'sfc'), ('msl', 'sfc'), ]
	plotname = 't2m_msl'

	def plot(self, data, static, dateinit, datevalid):
		done = plotter.plot(self, data, static, dateinit, datevalid)
		if done:
			return True

		overlays = [
			fig.map_overlay_contour(data['msl','sfc'], static, **conf.plot.merge('sfc', 'msl', 
				contour_labels=True, 
				contour_labels_format='%1.0f',
				contour_labels_scale=range(940,1060,10), 
				linewidths=[1], 
				scale=range(900,1070,2) ) ), 
			fig.map_overlay_contour(data['t2m','sfc'], static, **conf.plot.merge('sfc', 't2m',
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
		fig.map(data['t2m','sfc'], static, **plotconf)

		return True

# Surface fluxes, wind barbs, sea ice 
class shf_winds(ff10,flux):
	requires = [('u10', 'sfc'), ('v10', 'sfc'), ('sshf', 'sfc'), ('slhf', 'sfc'), ('sst', 'sfc'), ] # , ('ci', 'sfc')
	requires_diagnostic = [(ff10.cal_ff10, 'sfc'), (flux.cal_sensible, 'sfc'), (flux.cal_latent, 'sfc'), ]
	plotname = 'shf_winds'

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
			#fig.map_overlay_contour(data['ci','sfc'], static, **conf.plot.merge('sfc', 'ci',
			#	colors='royalblue',
			#	linewidths=[1],
			#	scale=[0.2, 0.8] ) ),
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

		plotconf = conf.plotf.merge('sfc', 'sshf',
				cmap=cm.BrBG,
				scale=shf,
				norm=mpl.colors.BoundaryNorm(shft, 256),
				extend='both',
				cb_tickspacing='uniform',
				overlays=overlays,
				**self.std_plotconf
		)
		fig.map(data['sshff','sfc']+data['slhff','sfc'], static, **plotconf)

		return True


# Near-surface relative humidity, total precipitation and MIZ
class rh2m_tp(precip,rh2m):
	requires = [('d2m', 'sfc'), ('t2m', 'sfc'), ('lsp', 'sfc'), ('cp', 'sfc'), ] #, ('ci', 'sfc')
	requires_diagnostic = [(precip.cal_crainrate, 'sfc'), 
				(precip.cal_lsrainrate, 'sfc'), 
				(precip.cal_trainrate, 'sfc'), 
				(rh2m.rh2m_from_d2m, 'sfc'), ]
	plotname = 'rh2m_tp'

	def plot(self, data, static, dateinit, datevalid):
		done = precip.plot(self, data, static, dateinit, datevalid)
		if done:
			return True

		s=[0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.4, 2.0, 3.0, 5.0, 7.0, 10.0] 
		st=[0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.4, 2.0, 3.0, 5.0, 7.0, 10.0, 1000.0] 
		overlays = [
			fig.map_overlay_shading(data['trr', 'sfc'], static, **conf.plotf.merge('sfc', 'trr',
				cmap=cm.trr, # Set a colormap
				norm=mpl.colors.BoundaryNorm(st, 256),
				cb_tickspacing='uniform',
				extend='max',
				alpha=0.5,
				scale=s,
				ticks=st,
				**self.std_plotconf ) ), 
			#fig.map_overlay_contour(data['SIC'], static, **conf.plot.merge('sfc', 'sic',
			#	colors='salmon',
			#	linewidths=[1],
			#	scale=[0.2, 0.8] ) ),
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
		fig.map(data['rh2m','sfc'], static, **plotconf)

		return True


# -----------------------------------------------------------------------------

# Most recent available data
now = dt.now()
if now.hour in range(11,23):
	forecast = dt(now.year,now.month,now.day,0)
else:
	forecast = dt(now.year,now.month,now.day,12)
	if now.hour < 11:
		forecast -= td(1,0)

# Override
#forecast = dt(2018,1,23,0)
plot_only_init = False

print('Plotting the ECMWF %s forecasts' % forecast.strftime('%Y-%m-%d %H'))

# Everything
plots = [
	t2m_msl(),
	shf_winds(), 
	rh2m_tp(),
]

if plot_only_init:
	datemask = np.zeros((25,), dtype='bool')
	datemask[0:2] = True
else:
	datemask = None

data = {}
for plot in plots:
	plot.error = False
	for q, plev in plot.requires:
		if (q,plev) not in data:
			try:
				f, dat_, static = metopen(conf.file_std % {'time': int(forecast.strftime(plotter.fmt)), 'plev': plev, 'q': conf.qf[q]}, q)
			except:
				print('Error loading data: ', (q, plev))
				plot.error = True
				continue
			
			if type(datemask) == type(None):
				datemask = np.ones((25,), dtype='bool')
				for tidx, date in zip(range(len(static.t)), static.t_parsed):
					#Plot only 3-hourly data to speed up diagnostic calculations and plotting
					if not date.hour % 3 == 0: #  or date.day > 18
						datemask[tidx] = False

			data[q,plev] = dat_[datemask,::].squeeze()
			f.close()
	
	static.t_parsed = static.t_parsed[datemask]

	if not plot.error:
		for fun, plev in plot.requires_diagnostic:
			fun(plot, data, plev, static)


import time

for tidx, date in zip(range(len(static.t)), static.t_parsed):
	data_inst = {}
	for q, plev in data:
		data_inst[q,plev] = data[q,plev][tidx]
	
	for plot in plots:
		plot.plot(data_inst, static, forecast, date)
		plt.close()
		
		# Temporarily delaying the plotting, to hopefully avoid random and obscure Permission denied errors.
		#time.sleep(0.5)


# the end
