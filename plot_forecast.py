#!/usr/bin/env python
# -*- encoding: utf-8

import matplotlib as mpl
mpl.use('Agg')
from dynlib import *
from settings import *


######################################################
# The base of _everything_

# Genering plot
class plotter(object):
	filetype = 'png'
	fcname = 'ec_for'
	opath = conf.opath
	
	# Add colorbar and legend
	decorations = False

	# Which data is required for the plot
	requires=[]
	requires_diagnostic = []
	fmt = '%Y%m%d%H'

	std_plotconf = {
		'm': proj.NAfcmap,
		'coastcolor': 'gray',
		'coast_alpha': 0.5,
		'grid_alpha': 0.25,
		'grid_linestyle': '-',
		'grid_latmax': 90,
		'show': False,
	}
	
	# Do the art; to be overriden in derived classes
	def plot(self, data, static, dateinit, datevalid):
		self.std_plotconf['save'] = '%s/%s_%s_from_%s_for_%s.%s' % (
				self.opath, self.fcname, self.plotname, 
				dateinit.strftime(self.fmt), datevalid.strftime(self.fmt), 
				self.filetype
		)

		if self.decorations:
			fi = plt.figure(figsize=(12.0,7.2), dpi=96)
			self.std_plotconf['show_legend'] = True
			
		else:
			fi = plt.figure(figsize=(10.8,7.2), dpi=96)
			self.std_plotconf['disable_cb'] = True

		fi.subplotpars.update(left=0.001, right=0.999, top=0.999, bottom=0.001)
		
		data_available = True
		for qplev in self.requires:
			data_available &= qplev in data

		if not data_available:
			fi.text(0.5, 0.5, 'Error: Data unavailable', horizontalalignment='center', fontsize=24, bbox=dict(facecolor='red', alpha=0.5))
			plt.savefig(self.std_plotconf['save'])
			return True

		else:
			return False


######################################################
# Plot archetypes

# Temperature shading and MSLP contours
class t_msl(plotter):
	pass

class t_wind(plotter):
	pass

# Geopotential shading and MSLP contours
class z_msl(plotter):
	pass

# Specific humidity and wind barbs
class q_wind(plotter):
	pass

# Potential vorticity and wind barbs
class pv_wind(plotter):
	pass

# Potential temperature and wind barbs
class pt_wind(plotter):
	pass

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


# Equivalent potential temperature
class the(plotter):
	def cal_the(self, data, plev, static):
		if not ('the', plev) in data:
			p = np.ones(data['q',plev].shape)*float(plev)*100
			data['the',plev] = dynlib.humidity.thetae_from_q(data['q',plev], data['t',plev], p, 
					static.dx, static.dy)


# Deformation
class deform(plotter):
	def cal_deform(self, data, plev, static):
		if not ('defabs', plev) in data:
			data['defabs',plev] = dynlib.diag.def_total(data['u',plev], data['v', plev], static.dx, static.dy)
		if not ('defang', plev) in data:
			data['defang',plev] = dynlib.diag.def_angle(data['u',plev], data['v', plev], static.dx, static.dy)


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


# Jets / Jet axes
class jets(ff):
	def cal_jetaxis(self, data, plev, static):
		dynlib.config.nsmooth = 5 
		dynlib.config.minlen = 2.0e6 
		dynlib.config.jetint_thres = 0.5e-8
		dynlib.config.searchrad = 1.5
		
		if not ('jetaxis', plev) in data:
			data['jetaxis',plev], data['jaoff',plev] = dynlib.detect.jetaxis(10000, 1000, 
					data['u',plev], data['v',plev], static.dx, static.dy)



######################################################
# Specific plots

# Temperature@850hPa shading and MSLP contours
class t850_msl(t_msl):
	requires = [('t', '850'), ('msl', 'sfc')]
	plotname = 't850_msl'

	def plot(self, data, static, dateinit, datevalid):
		done = t_msl.plot(self, data, static, dateinit, datevalid)
		if done:
			return True

		overlays = [
			fig.map_overlay_dat(data['msl','sfc']/100, static, **conf.contour.merge('default', 
				contour_labels=True, 
				contour_labels_format='%1.0f',
				contour_labels_scale=range(940,1060,15), 
				linewidths=[1], 
				scale=range(900,1070,5) ) ), 
			fig.map_overlay_dat(data['t','850']-273.15, static, **conf.contour.merge('default', 
				linewidths=[1], 
				linestyles='dashed',
				scale=range(0,2,2) ) ),
		]
		plotconf = conf.contourf.merge('t',
				overlays=overlays,
				cmap=cm.t, # Set a colormap
				scale=range(-34,36,2),
				ticks=range(-30,31,10),
				**self.std_plotconf
		)
		fig.map_oro_dat(data['t', '850']-273.15, static, **plotconf)

		return True


# Equivelent potential temperature@850hPa shading and wind barbs
class the850_wind(the):
	requires = [('t', '850'), ('q', '850'), ('u', '850'), ('v', '850')]
	requires_diagnostic = [(the.cal_the, '850'), ]
	plotname = 'the850_wind'

	def plot(self, data, static, dateinit, datevalid):
		done = the.plot(self, data, static, dateinit, datevalid)
		if done:
			return True

		plotconf = conf.contourf.merge('t',
				cmap=cm.t, # Set a colormap
				scale=np.arange(250,351,2.5),
				ticks=range(250,351,10),
				**self.std_plotconf
		)
		fig.map_oro_barb(data['u','850'], data['v','850'], static, dat=data['the', '850'], **plotconf)

		return True


# Geopotential@850hPa shading and MSLP contours
class z500_msl(z_msl):
	requires = [('z', '500'), ('msl', 'sfc')]
	plotname = 'z500_msl'

	def plot(self, data, static, dateinit, datevalid):
		done = z_msl.plot(self, data, static, dateinit, datevalid)
		if done:
			return True

		overlays = [
			fig.map_overlay_dat(data['msl','sfc']/100, static, **conf.contour.merge('default', 
				contour_labels=True, 
				linewidths=[1], 
				scale=range(900,1070,5) ) ),
			fig.map_overlay_dat(data['z','500']/98.0665, static, **conf.contour.merge('default', 
				contour_labels=True, 
				colors='white',
				linewidths=[1],
				linestyles='dashed',
				scale=range(472,601,16) ) ),
			fig.map_overlay_dat(data['z','500']/98.0665, static, **conf.contour.merge('default', 
				contour_labels=True, 
				colors='white',
				linewidths=[2],
				scale=range(552,554,2) ) ), 
		]
		plotconf = conf.contourf.merge('z',
				overlays=overlays,
				cmap=cm.z,
				scale=range(476,604,4),
				ticks=range(480,601,20),
				**self.std_plotconf
		)
		fig.map_oro_dat(data['z','500'], static, **plotconf)

		return True


# Specific humidity@850hPa shading and wind barbs
class q850_wind(precip):
	requires = [('q', '850'), ('u', '850'), ('v', '850'), ('cp', 'sfc'), ('lsp', 'sfc')]
	requires_diagnostic = [ (precip.cal_crainrate, 'sfc'), 
				(precip.cal_lsrainrate, 'sfc') ]
	plotname = 'q850_wind'

	def plot(self, data, static, dateinit, datevalid):
		done = precip.plot(self, data, static, dateinit, datevalid)
		if done:
			return True

		overlays=[fig.map_overlay_dat(data['crr','sfc']*1000, static, **conf.contour.merge('default', 
				scale=[1.0, 3.0, 10.0],
				colors='c', ) ), 
			 fig.map_overlay_dat(data['lsrr','sfc']*1000, static, **conf.contour.merge('default', 
				scale=[1.0, 3.0, 10.0],
				colors='m', ) ), 
		]

		plotconf = conf.contourf.merge('q',
				overlays=overlays,
				cmap=cm.q,
				scale=np.arange(0,16,1),
				ticks=range(0,16,5),
				extend='max',
				**self.std_plotconf
		)
		fig.map_oro_barb(data['u','850'], data['v','850'], static, dat=data['q','850'], **plotconf) 

		return True


# Potential vorticity@300K shading and wind barbs
class pvpt300_wind_npolar(pv_wind):
	requires = [('pv', 'pt300'), ('u', 'pt300'), ('v', 'pt300')]
	plotname = 'pvpt300_wind'
	opath = pv_wind.opath+'_npolar'

	def plot(self, data, static, dateinit, datevalid):
		done = pv_wind.plot(self, data, static, dateinit, datevalid)
		if done:
			return True

		overlays=[fig.map_overlay_dat(data['pv','pt300']*1e6, static, **conf.contour.merge('pv', 
				contour_labels=True, 
				linewidths=[1.5],
				scale=range(2,3,1) ) ), 
		]
		s=[0, 1.0,  2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
		st=[0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
		plotconf = conf.contourf.merge('pv',
				overlays=overlays,
				cmap=cm.pv_new,
				norm=mpl.colors.BoundaryNorm(s, 256),
				scale=s,
				ticks=st,
				**self.std_plotconf
		)
		fig.map_oro_barb(data['u','pt300'], data['v','pt300'], static, dat=data['pv','pt300']*1e6, **plotconf) 

		return True


# Potential vorticity@350K shading and wind barbs
class pvpt330_wind_npolar(pv_wind):
	requires = [('pv', 'pt330'), ('u', 'pt330'), ('v', 'pt330')]
	plotname = 'pvpt330_wind'
	opath = pv_wind.opath+'_npolar'

	def plot(self, data, static, dateinit, datevalid):
		done = pv_wind.plot(self, data, static, dateinit, datevalid)
		if done:
			return True

		overlays=[fig.map_overlay_dat(data['pv','pt330']*1e6, static, **conf.contour.merge('pv', 
				contour_labels=True, 
				linewidths=[1.5],
				scale=range(2,3,1) ) ), 
		]
		s=[0, 1.0,  2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
		st=[0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
		plotconf = conf.contourf.merge('pv',
				overlays=overlays,
				cmap=cm.pv_new,
				norm=mpl.colors.BoundaryNorm(s, 256),
				scale=s,
				ticks=st,
				**self.std_plotconf
		)
		fig.map_oro_barb(data['u','pt330'], data['v','pt330'], static, dat=data['pv','pt330']*1e6, **plotconf) 

		return True


# Potential vorticity@350K shading and wind barbs
class pvpt350_wind_npolar(pv_wind):
	requires = [('pv', 'pt350'), ('u', 'pt350'), ('v', 'pt350')]
	plotname = 'pvpt350_wind'
	opath = pv_wind.opath+'_npolar'

	def plot(self, data, static, dateinit, datevalid):
		done = pv_wind.plot(self, data, static, dateinit, datevalid)
		if done:
			return True

		overlays=[fig.map_overlay_dat(data['pv','pt350']*1e6, static, **conf.contour.merge('pv', 
				contour_labels=True, 
				linewidths=[1.5],
				scale=range(2,3,1) ) ), 
		]
		s=[0, 1.0,  2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
		st=[0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
		plotconf = conf.contourf.merge('pv',
				overlays=overlays,
				cmap=cm.pv_new,
				norm=mpl.colors.BoundaryNorm(s, 256),
				scale=s,
				ticks=st,
				**self.std_plotconf
		)
		fig.map_oro_barb(data['u','pt350'], data['v','pt350'], static, dat=data['pv','pt350']*1e6, **plotconf) 

		return True


# Potential vorticity@300K shading and wind barbs
class pvpt300_wind(pv_wind):
	requires = [('pv', 'pt300'), ('u', 'pt300'), ('v', 'pt300')]
	plotname = 'pvpt300_wind'

	def plot(self, data, static, dateinit, datevalid):
		done = pv_wind.plot(self, data, static, dateinit, datevalid)
		if done:
			return True

		overlays=[fig.map_overlay_dat(data['pv','pt300']*1e6, static, **conf.contour.merge('pv', 
				contour_labels=True, 
				linewidths=[1.5],
				scale=range(2,3,1) ) ), 
		]
		s=[0, 1.0,  2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
		st=[0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
		plotconf = conf.contourf.merge('pv',
				overlays=overlays,
				cmap=cm.pv_new,
				norm=mpl.colors.BoundaryNorm(s, 256),
				scale=s,
				ticks=st,
				**self.std_plotconf
		)
		fig.map_oro_barb(data['u','pt300'], data['v','pt300'], static, dat=data['pv','pt300']*1e6, **plotconf) 

		return True


# Potential vorticity@300K shading and wind barbs
class pvpt315_wind(pv_wind):
	requires = [('pv', 'pt315'), ('u', 'pt315'), ('v', 'pt315')]
	plotname = 'pvpt315_wind'

	def plot(self, data, static, dateinit, datevalid):
		done = pv_wind.plot(self, data, static, dateinit, datevalid)
		if done:
			return True

		overlays=[fig.map_overlay_dat(data['pv','pt315']*1e6, static, **conf.contour.merge('pv', 
				contour_labels=True, 
				linewidths=[1.5],
				scale=range(2,3,1) ) ), 
		]
		s=[0, 1.0,  2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
		st=[0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
		plotconf = conf.contourf.merge('pv',
				overlays=overlays,
				cmap=cm.pv_new,
				norm=mpl.colors.BoundaryNorm(s, 256),
				scale=s,
				ticks=st,
				**self.std_plotconf
		)
		fig.map_oro_barb(data['u','pt315'], data['v','pt315'], static, dat=data['pv','pt315']*1e6, **plotconf) 

		return True


# Potential vorticity@350K shading and wind barbs
class pvpt330_wind(pv_wind):
	requires = [('pv', 'pt330'), ('u', 'pt330'), ('v', 'pt330')]
	plotname = 'pvpt330_wind'

	def plot(self, data, static, dateinit, datevalid):
		done = pv_wind.plot(self, data, static, dateinit, datevalid)
		if done:
			return True

		overlays=[fig.map_overlay_dat(data['pv','pt330']*1e6, static, **conf.contour.merge('pv', 
				contour_labels=True, 
				linewidths=[1.5],
				scale=range(2,3,1) ) ), 
		]
		s=[0, 1.0,  2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
		st=[0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
		plotconf = conf.contourf.merge('pv',
				overlays=overlays,
				cmap=cm.pv_new,
				norm=mpl.colors.BoundaryNorm(s, 256),
				scale=s,
				ticks=st,
				**self.std_plotconf
		)
		fig.map_oro_barb(data['u','pt330'], data['v','pt330'], static, dat=data['pv','pt330']*1e6, **plotconf) 

		return True


# Potential vorticity@350K shading and wind barbs
class pvpt350_wind(pv_wind):
	requires = [('pv', 'pt350'), ('u', 'pt350'), ('v', 'pt350')]
	plotname = 'pvpt350_wind'

	def plot(self, data, static, dateinit, datevalid):
		done = pv_wind.plot(self, data, static, dateinit, datevalid)
		if done:
			return True

		overlays=[fig.map_overlay_dat(data['pv','pt350']*1e6, static, **conf.contour.merge('pv', 
				contour_labels=True, 
				linewidths=[1.5],
				scale=range(2,3,1) ) ), 
		]
		s=[0, 1.0,  2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
		st=[0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
		plotconf = conf.contourf.merge('pv',
				overlays=overlays,
				cmap=cm.pv_new,
				norm=mpl.colors.BoundaryNorm(s, 256),
				scale=s,
				ticks=st,
				**self.std_plotconf
		)
		fig.map_oro_barb(data['u','pt350'], data['v','pt350'], static, dat=data['pv','pt350']*1e6, **plotconf) 

		return True


# Potential temperature@PV2 shading and wind barbs
class ptpv2_wind(pt_wind):
	requires = [('pt', 'pv2000'), ('u', 'pv2000'), ('v', 'pv2000')]
	plotname = 'ptpv2_wind'

	def plot(self, data, static, dateinit, datevalid):
		done = pt_wind.plot(self, data, static, dateinit, datevalid)
		if done:
			return True
		
		plotconf = conf.contourf.merge('pt',
				overlays=[],
				cmap=cm.t,
				scale=np.arange(270,396,5),
				ticks=[270,285,300,315,330,350,370,395],
				**self.std_plotconf
		)
		fig.map_oro_barb(data['u', 'pv2000'], data['v', 'pv2000'], static, dat=data['pt', 'pv2000'], **plotconf)

		return True


# Potential temperature@PV2 shading and wind barbs
class ptpv2_wind_npolar(pt_wind):
	requires = [('pt', 'pv2000'), ('u', 'pv2000'), ('v', 'pv2000')]
	plotname = 'ptpv2_wind' 
	opath = pt_wind.opath+'_npolar'

	def plot(self, data, static, dateinit, datevalid):
		done = pt_wind.plot(self, data, static, dateinit, datevalid)
		if done:
			return True
		
		plotconf = conf.contourf.merge('pt',
				overlays=[],
				cmap=cm.t,
				scale=np.arange(270,396,5),
				ticks=[270,285,300,315,330,350,370,395],
				**self.std_plotconf
		)
		fig.map_oro_barb(data['u', 'pv2000'], data['v', 'pv2000'], static, dat=data['pt', 'pv2000'], **plotconf)

		return True


# Total precipitation
class tp(precip):
	requires = [('cp', 'sfc'), ('lsp', 'sfc')]
	requires_diagnostic = [ (precip.cal_crainrate, 'sfc'), 
				(precip.cal_lsrainrate, 'sfc'), 
				(precip.cal_trainrate, 'sfc') ]
	plotname = 'tp'

	def plot(self, data, static, dateinit, datevalid):
		done = precip.plot(self, data, static, dateinit, datevalid)
		if done:
			return True

		s=[0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.4, 2.0, 3.0, 5.0, 7.0, 10.0] 
		st=[0, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.4, 2.0, 3.0, 5.0, 7.0, 10.0, 1000.0] 
		plotconf = conf.contourf.merge('tp', 	# Get configuration for q, but override with the other arguments, like
				cmap=cm.prec_bl, # Set a colormap
				norm=mpl.colors.BoundaryNorm(st, 256),
				cb_tickspacing='uniform',
				extend='max',
				scale=s,
				ticks=s,
				**self.std_plotconf
		)
		fig.map_oro_dat(data['trr','sfc']*1000+1e-10, static, **plotconf)

		return True


# Total column water vapour
class tcwv(precip,iwvtrans):
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

		overlays=[fig.map_overlay_dat(data['crr','sfc']*1000, static, **conf.contour.merge('default', 
				scale=[0.3, 1.0, 3.0],
				colors='c', ) ), 
			 fig.map_overlay_dat(data['lsrr','sfc']*1000, static, **conf.contour.merge('default', 
				scale=[0.3, 1.0, 3.0],
				colors='m', ) ), 
		]

		plotconf = conf.contourf.merge('tcwv', 	# Get configuration for q, but override with the other arguments, like
				overlays=overlays,
				cmap=cm.q,
				scale=range(4,45,2),
				ticks=range(10,41,10),
				quiver=True,
				quiver_length=1.5,
				**self.std_plotconf
		)
		fig.map_oro_barb(data['iwvtransx','sfc'], data['iwvtransy','sfc'], static, dat=data['tcwv','sfc'], **plotconf)

		return True


# Total column water vapour
class tcwv_npolar(plotter):
	requires = [('tcwv', 'sfc'), ]
	plotname = 'tcwv'
	opath = pt_wind.opath+'_npolar'

	def plot(self, data, static, dateinit, datevalid):
		done = plotter.plot(self, data, static, dateinit, datevalid)
		if done:
			return True

		plotconf = conf.contourf.merge('tcwv', 	# Get configuration for q, but override with the other arguments, like
				cmap=cm.q,
				scale=range(6,61,3),
				ticks=range(15,61,15),
				**self.std_plotconf
		)
		fig.map_oro_dat(data['tcwv','sfc'], static, **plotconf)

		return True


# Total cloud cover
class tcc(plotter):
	requires = [('tcc', 'sfc'), ]
	plotname = 'tcc'

	def plot(self, data, static, dateinit, datevalid):
		done = plotter.plot(self, data, static, dateinit, datevalid)
		if done:
			return True

		s = np.array([0,] + list(np.arange(0.0625,0.95,0.125)) + [1,])
		t = (s[1:]+s[:-1])/2.0
		plotconf = conf.contourf.merge('tcc', 	# Get configuration for q, but override with the other arguments, like
				cmap=cm.q_r, # Set a colormap
				scale=s,
				ticks=t,
				ticklabels=["0/8","1/8", "2/8", "3/8", "4/8", "5/8", "6/8", "7/8", "8/8"],
				extend='neither',
				**self.std_plotconf
		)
		fig.map_oro_dat(data['tcc','sfc'], static, **plotconf)

		return True


# Near surface winds.
class ff10_wind(ff10):
	requires = [('u10', 'sfc'), ('v10', 'sfc')]
	requires_diagnostic = [(ff10.cal_ff10, 'sfc'), ]
	plotname = 'ff10_wind' 

	def plot(self, data, static, dateinit, datevalid):
		done = plotter.plot(self, data, static, dateinit, datevalid)
		if done:
			return True
		
		s = np.arange(5.0,32.6,2.5)
		plotconf = conf.contourf.merge('u', 	# Get configuration for q, but override with the other arguments, like
				cmap=cm.ff, 
				scale=s,
				extend='both',
				**self.std_plotconf
		)
		fig.map_oro_barb(data['u10','sfc'], data['v10','sfc'], static, dat=data['ff10','sfc'], **plotconf)

		return True


# Near surface winds.
class ff850_wind(ff):
	requires = [('u', '850'), ('v', '850')]
	requires_diagnostic = [(ff.cal_ff, '850'), ]
	plotname = 'ff850_wind'

	def plot(self, data, static, dateinit, datevalid):
		done = plotter.plot(self, data, static, dateinit, datevalid)
		if done:
			return True

		s=np.arange(10.0,46.0,2.5)
		plotconf = conf.contourf.merge('u', 	# Get configuration for q, but override with the other arguments, like
				cmap=cm.ff, # Set a colormap
				scale=s,
				extend='both',
				**self.std_plotconf
		)
		fig.map_oro_barb(data['u','850'], data['v','850'], static, dat=data['ff','850'], **plotconf)

		return True


# Near surface winds.
class deform850_msl(deform):
	requires = [('u', '850'), ('v', '850'), ('msl', 'sfc')]
	requires_diagnostic = [(deform.cal_deform, '850'), ]
	plotname = 'deform850_msl'

	def plot(self, data, static, dateinit, datevalid):
		done = plotter.plot(self, data, static, dateinit, datevalid)
		if done:
			return True

		overlays = [
			fig.map_overlay_dat(data['msl','sfc']/100, static, **conf.contour.merge('default', 
				contour_labels=True, 
				contour_labels_format='%1.0f',
				contour_labels_scale=range(940,1060,20), 
				linewidths=[1], 
				colors='b',
				alpha=0.7,
				scale=range(900,1070,10) ) ), 
		]

		s=np.arange(10,46,2.5)
		plotconf = conf.contourf.merge('defabs', 	# Get configuration for q, but override with the other arguments, like
				overlays=overlays,
				scale=np.arange(6,31,3),
				**self.std_plotconf
		)
		fig.map_oro_deform(data['defabs','850'], data['defang','850'], static, **plotconf)

		return True


# Near surface winds.
class ffpv2_wind(jets):
	requires = [('u', 'pv2000'), ('v', 'pv2000')]
	requires_diagnostic = [(jets.cal_ff, 'pv2000'), (jets.cal_jetaxis, 'pv2000'), ]
	plotname = 'ffpv2_wind'

	def plot(self, data, static, dateinit, datevalid):
		done = plotter.plot(self, data, static, dateinit, datevalid)
		if done:
			return True
		
		overlays = [
			fig.map_overlay_lines(data['jetaxis','pv2000'], data['jaoff','pv2000'], static, linecolor='k', linewidth=6), 
			fig.map_overlay_lines(data['jetaxis','pv2000'], data['jaoff','pv2000'], static, linecolor='w', linewidth=4), 
		]

		plotconf = conf.contourf.merge('u', 	# Get configuration for q, but override with the other arguments, like
				cmap=cm.ff, 
				scale=np.arange(15,76,5),
				ticks=np.arange(15,76,15),
				extend='both',
				overlays=overlays,
				**self.std_plotconf
		)
		fig.map_oro_barb(data['u','pv2000'], data['v','pv2000'], static, dat=data['ff','pv2000'], **plotconf)

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

plot_only_init = False

plots = [t850_msl(), z500_msl(), the850_wind(), q850_wind(), deform850_msl(), 
		pvpt300_wind(), pvpt315_wind(), pvpt330_wind(), pvpt350_wind(), 
		ptpv2_wind(), tcwv(), tcc(), tp(), ff10_wind(), ffpv2_wind(), ff850_wind(), 
		pvpt300_wind_npolar(), pvpt330_wind_npolar(), pvpt350_wind_npolar(), 
		ptpv2_wind_npolar(), tcwv_npolar(),
]

data = {}
for plot in plots:
	plot.error = False
	for q, plev in plot.requires:
		if (q,plev) not in data:
			try:
				f, dat_, static = metopen(conf.file_std % {'time': int(forecast.strftime(plotter.fmt)), 'plev': plev, 'q': conf.qi[q]}, q)
			except RuntimeError:
				print 'Error loading data: ', (q, plev)
				plot.error = True
				continue

			data[q,plev] = dat_[::]
			f.close()

	for fun, plev in plot.requires_diagnostic:
		if not plot.error:
			fun(plot, data, plev, static)

			

for tidx, date in zip(range(len(static.t)), static.t_parsed):
	# Plot only 3-hourly data to speed up plotting
	if not date.hour % 3 == 0:
		continue

	# Plot only initial time step
	if plot_only_init and not date == forecast:
		continue

	data_inst = {}
	for q, plev in data:
		data_inst[q,plev] = data[q,plev][tidx]
	
	for plot in plots:
		plot.plot(data_inst, static, forecast, date)
		plt.close()


# the end
