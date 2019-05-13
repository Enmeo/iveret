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

from scipy.ndimage.filters import gaussian_filter
from math import radians, cos, sin, asin, sqrt, pow

######################################################
# The base of _everything_

#Register slope
slopevar = ('slope', 'slope', 'Isentropic slope', 'm/km')
conf.register_variable([slopevar], ['200-600','600-900'])

#############
dynlib.dynfor.config.thres_min_dzdth = 5e-4 #1e-3 #-10000 #1e-3
dynlib.dynfor.config.thres_min_slope = 1e-100
dynlib.dynfor.config.thres_max_slope = 1e100
dynlib.dynfor.config.grid_cyclic_ew  = False

def magma_new():
                ''' Colorbar for slope, changed from the magma colorbar, but with white instead of yello
                    Returns
                    -------
                    mpl.colors.LinearSegmentedColormap
                    Colormap
                '''
                cdict = {'red':   ((0.0, 1.0, 1.0), (0.25,0.985693,0.985693), (0.5, 0.716387, 0.716387), (0.75,0.316654,0.316654), (1.0, 0.001462, 0.001462)),
                        'green': ((0.0, 1.0, 1.0), (0.25,0.528148,0.528148), (0.5, 0.214982, 0.214982), (0.75,0.071690,0.071690), (1.0, 0.000466, 0.000466)),
                        'blue':  ((0.0, 1.0, 1.0), (0.25,0.379371,0.379371), (0.5, 0.475290, 0.475290), (0.75,0.485380,0.485380), (1.0, 0.013866, 0.013866))  }

                return mpl.colors.LinearSegmentedColormap('magma_new',cdict,256)


conf.plotf[None, 'slope', 'cmap'] = magma_new

# Genering plot
class plotter(object):
	filetype = 'png'
	fcname = 'ec_for'
	
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
			#conf.plotpathTemp = "/home/chriswei/Figures/"
			plt.savefig(conf.plotpath + '/' + self.std_plotconf['save'])
			#plt.savefig(conf.plotpathTemp + '/' + self.std_plotconf['save'])
			return True

		else:
			return False


######################################################
# Plot archetypes

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

#Class for plotting slope
class slope(plotter):
	# plev must be descending order
	def cal_slope(self,data,plevs,static):
		if not ('slope_up') in data:
			#Define dp
			plev_fl = []
			dp = np.zeros(data['u'].shape)
			for k in range(len(plevs)):
				plev_fl.append(float(plevs[k]))
				##print(k)
				if k == 0 or k == len(plevs) - 1:
					dp[:,k,::] = 0
				else:
					dp[:,k,::] = float(plevs[k+1]) - float(plevs[k-1])

			#TO DO: Smooth data before?

			#Call slope_prepare_pres
			dynlib.dynfor.tend.slope_prepare_pres(data['z']/9.81, plev_fl, data['t'], data['w'], static.dx, static.dy, dp)

			#TO DO: Calculate tilting

			#Masked array needed for vertical integration
			clean_slope    = np.ma.masked_array(dynlib.dynfor.tend.slope,np.isnan(dynlib.dynfor.tend.slope))

			#Vertical integration + change units from m/m to m/km
			slope_low  = np.array(np.ma.average(clean_slope[:,0:6,::],axis=1,weights=dp[0,0:6,0,0])*1000.0)
			#slope_up
			slope_up = np.array(np.ma.average(clean_slope[:,5:11,::],axis=1,weights=dp[0,5:11,0,0])*1000.0)

			#Define jet 			
			jet = (data['u'][:,9,::]**2.0 + data['v'][:,9,::]**2.0)**0.5
			
			#Total precip
			#tp = data['cp'] + data['lsp']

			#Total fluxes 
			#sflux = data['sshf']  + data['slhf']

			#Define arrays for filtering
			slope_up_filt = np.zeros(slope_up.shape)
			slope_low_filt = np.zeros(slope_low.shape)
			jet_filt = np.zeros(jet.shape)
			#tp_filt = np.zeros(tp.shape)
			#sflux_filt = np.zeros(sflux.shape)

			#Delete masked array
			del(clean_slope)

			#Filter data using a Gaussian smoothing, with a standard deviation of sigma_dist
			R = 6371.0  # radius of the earth in km
			for latidx in range(static.x.shape[0]):
				print("Latidx" + str(latidx))
				for lonidx in range(static.x.shape[1]):

					#Calculate distances
					dists = np.zeros([17,17]) 
					for lonidx2 in range(17):
						for latidx2 in range(17):
							dists[latidx2,lonidx2] = np.nan
							if((lonidx + lonidx2 -8 >= 0) & (lonidx + lonidx2 - 8 < 421) & (latidx + latidx2 - 8  >= 0) & (latidx + latidx2 - 8  < 151)):
								#Pythagoras
								lat1_radians = radians(static.y[latidx,lonidx])
								lat2_radians = radians(static.y[latidx+latidx2-8,lonidx+lonidx2-8])
								dlon = radians(lonidx2-8.0)*0.5 #lon2_radians - lon1_radians
								dlat = radians(latidx2-8.0)*0.5 #lat2_radians - lat1_radians
								#a = (sin(dlat/2))**2.0 + cos(lat1_radians) * cos(lat2_radians) * (sin(dlon/2.0))**2.0
								#c = 2.0 * asin(np.nanmin([1,sqrt(a)]))
								#dists[latidx2,lonidx2]  = R *c
								#Pythagoras
								x = dlon * cos( 0.5*(lat1_radians + lat2_radians) )
								y = dlat
								dists[latidx2,lonidx2]  = R * sqrt( x*x + y*y )


					#Calculate weights
					sigma_dist  = 100.0
					weights = np.e**(-dists**2.0/(sigma_dist)**2.0*1.0/2.0)
					weights = weights/np.nansum(weights)

					#Apply weights to smooth data
					for tidx in range(data['u'].shape[0]):
						if((lonidx -8 >= 0) & (lonidx + 9 < 421) & (latidx - 8  >= 0) & (latidx +  9  < 151)):
							#Filter slope variables
							slope_up_filt[tidx,latidx,lonidx] = np.nansum(slope_up[tidx,(latidx -8):(latidx + 9), (lonidx -8):(lonidx + 9)]*weights)
							#ave_tilt_filt[tidx,latidx,lonidx] = np.nansum(ave_tilt_ar[tidx,(latidx -8):(latidx + 9), (lonidx -8):(lonidx + 9)]*weights)
							slope_low_filt[tidx,latidx,lonidx] = np.nansum(slope_low[tidx,(latidx -8):(latidx + 9), (lonidx -8):(lonidx + 9)]*weights)
							#ave_ltilt_filt[tidx,latidx,lonidx] = np.nansum(ave_ltilt_ar[tidx,(latidx -8):(latidx + 9), (lonidx -8):(lonidx + 9)]*weights)

							#Other variables
							jet_filt[tidx,latidx,lonidx] = np.nansum(jet[tidx,(latidx -8):(latidx + 9), (lonidx -8):(lonidx + 9)]*weights)
							#tp_filt[tidx,latidx,lonidx] = np.nansum(tp[tidx,(latidx -8):(latidx + 9), (lonidx -8):(lonidx + 9)]*weights)
							#lsp_filt[tidx,latidx,lonidx] = np.nansum(lsp[tidx,(latidx -8):(latidx + 9), (lonidx -8):(lonidx + 9)]*weights)
							#sflux_filt[tidx,latidx,lonidx] = np.nansum(shf[tidx,(latidx -8):(latidx + 9), (lonidx -8):(lonidx + 9)]*weights)

			#Save data
			data['slope_up'] = slope_up_filt
			data['slope_low'] = slope_low_filt
			data['jet'] = jet_filt
			#data['tp']  = tp_filt
			#data['sflux'] = sflux_filt

######################################################
# Specific plots
#plevs = ['925','900','850','800','700','600','500','400','300','200']

# Total column water vapour
class upperslope(slope):
	#requires = [('tcwv', 'sfc'), ('cp', 'sfc'), ('lsp', 'sfc'), ('slhf','sfc'),('sshf','sfc'),
	#		('u', '925'), ('v', '925'), ('w','925'),('z','925'),('t','925'), ('q', '925'), 
        #                ('u', '900'), ('v', '900'), ('w','900'),('z','900'),('t','900'),  
	#		('u', '850'), ('v', '850'), ('w','850'),('z','850'),('t','850'), ('q', '850'),
        #                ('u', '800'), ('v', '600'), ('w','800'),('z','800'),('t','800'), 
        #                ('u', '700'), ('v', '700'), ('w','700'),('z','700'),('t','700'), ('q', '700'),
        #                ('u', '600'), ('v', '600'), ('w','600'),('z','600'),('t','600'),
        #                ('u', '500'), ('v', '500'), ('w','500'),('z','500'),('t','500'), ('q', '500'),
        #                ('u', '400'), ('v', '400'), ('w','400'),('z','400'),('t','400'),
        #                ('u', '300'), ('v', '300'), ('w','300'),('z','300'),('t','300'), ('q', '300'),
        #                ('u', '200'), ('v', '200'), ('w','200'),('z','200'),('t','200')
	#]

	#Required variables
	requires = ["u","v","w","z","t"] #Required variables on plevs
	plevs    = ["925","900","850","800","700","600","500","400","300","200"]
	requires_sfc = ["cp","lsp"] #Required surface variables        
        
	#Required diagnostic   
	requires_diagnostic = [(slope.cal_slope, ['925','900','850','800','700','600','500','400','300','200']),]

	plotname = 'slope_upper'

	def plot(self, data, static, dateinit, datevalid):
		done = plotter.plot(self, data, static, dateinit, datevalid)
		if done:
			return True
		
		overlays = [
		#       fig.map_overlay_quiver(data['iwvtransx','sfc'], data['iwvtransy','sfc'], static, 
		#               **conf.plot.merge('sfc', 'tcwv', linewidths=0.2) ),
			fig.map_overlay_contour(data['jet'], static, **conf.plot.merge('pv2000', 'ff',
				linewidths=[2.0],
				linestyles='solid',
				colors='black',
				scale=np.arange(30,91,15) ) ),
		]

		plotconf = conf.plotf.merge('200-600', 'slope',
				overlays=overlays,
				scale=np.arange(2,10.1,0.25),
				#ticks=np.arange(2,9,0.5),
				#quiver=True,
				#quiver_length=1.5,
				**self.std_plotconf
		)
		fig.map(data['slope_up'], static, **plotconf)

		return True

class lowerslope(slope):

	#Required variables
        requires = ["u","v","w","z","t"]
        plevs    = ["925","900","850","800","700","600","500","400","300","200"]
        requires_sfc = ["sshf","slhf"]

	#Required diagnostic
        requires_diagnostic = [(slope.cal_slope, ['925','900','850','800','700','600','500','400','300','200']),]

        plotname = 'slope_lower'

        def plot(self, data, static, dateinit, datevalid):
                done = plotter.plot(self, data, static, dateinit, datevalid)
                if done:
                        return True

                overlays = [
                #       fig.map_overlay_quiver(data['iwvtransx','sfc'], data['iwvtransy','sfc'], static, 
                #               **conf.plot.merge('sfc', 'tcwv', linewidths=0.2) ),
                        fig.map_overlay_contour(data['jet'], static, **conf.plot.merge('pv2000', 'ff',
                                linewidths=[2.0],
                                linestyles='solid',
                                colors='black',
                                scale=np.arange(30,91,15) ) ),
                        #fig.map_overlay_contour(data['tp'], static, **conf.plot.merge('pv2000', 'ff',
                        #        linewidths=[2.0],
                        #        linestyles='solid',
                        #        colors='black',
                        #        scale=np.arange(30,91,15) ) ),
		]
                


                #overlays = [
                #        fig.map_overlay_contour(data['ff_smooth','pv2000'], static, **conf.plot.merge('pv2000', 'ff',
                #                scale=np.arange(30,91,15),
                #        ) ),
                #        fig.map_overlay_lines(data['jetaxis','pv2000'], data['jaoff','pv2000'], static, linecolor='k', linewidth=6),
                #        fig.map_overlay_lines(data['jetaxis','pv2000'], data['jaoff','pv2000'], static, linecolor='w', linewidth=4),
                #]

                plotconf = conf.plotf.merge('600-900', 'slope',
                                overlays=overlays,
                                scale=np.arange(2,10.1,0.25),
                                #ticks=np.arange(2,9,0.5),
                                #quiver=True,
                                #quiver_length=1.5,
                                **self.std_plotconf
                )
                fig.map(data['slope_low'], static, **plotconf)

                return True




# -----------------------------------------------------------------------------

forecast = get_current_fc()
# Optional: Override
#forecast = dt(2019,3,12,12)
plot_only_init = False

#forecast = forecast - td(days=1)

print('Plotting the ECMWF %s forecasts' % forecast.strftime('%Y-%m-%d %H'))

# Everything
PLOTS = {
	'plev': [
		upperslope(), lowerslope(),
	], 
}

import sys

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
	datemask = None

data = {}
for plot in plots:
	plot.error = False

	#Get variables on pressure levels
	for q in plot.requires:
		if q not in data:			
			temp = np.zeros([53,len(plot.plevs),151,421])
			for plevidx in range(len(plot.plevs)):				
				plev = plot.plevs[plevidx]

				try:
					f, dat_, static_ = metopen(conf.file_std % {'time': int(forecast.strftime(plotter.fmt)), 'plev': plev, 'q': conf.qf[q]}, q)
					static_whole = static_
					if len(dat_.shape)==4:
						dat_ = dat_[:,:,0:151,90:511]
					elif len(dat_.shape)==3:
						dat_ = dat_[:,0:151,90:511]
					#Close file
					f.close()
				except:
					#try:	
					add_file_pattern = '%(time)d/ec.for-NA.%(time)d.%(plev)s.%(q)s'
					f, dat_, static = metopen(add_file_pattern % {'time': int(forecast.strftime(plotter.fmt)), 'plev': plev, 'q': conf.qf[q]}, q)
					static_ = static
					#except:
					#	print('Error loading data: ', (q, plev))
					#	plot.error = True
					#	continue
					#Close file
					f.close()
				temp[:,plevidx,::] = dat_[::].squeeze()

			if type(datemask) == type(None):
				datemask = np.ones((53,), dtype='bool')
				for tidx, date in zip(range(len(static_.t)), static_.t_parsed):
					#Plot only 3-hourly data to speed up diagnostic calculations and plotting
					if not date.hour % 3 == 0: #  or date.day > 18
						datemask[tidx] = False

			temp = temp[datemask,::].squeeze()
			##close file
			#f.close()
			data[q] = temp
			del(temp)

	#Get surface variables
	for q in plot.requires_sfc:
		if q not in data:
			try:
				plev = "sfc"
				f, dat_, static_ = metopen(conf.file_std % {'time': int(forecast.strftime(plotter.fmt)), 'plev': plev, 'q': conf.qf[q]}, q)
				static_whole = static_
				if len(dat_.shape)==4:
					data[q] = dat_[:,:,0:151,90:511]
				elif len(dat_.shape)==3:
					data[q] = dat_[:,0:151,90:511]
				f.close()
			except:
                                print('Error loading data: ', q)
                                plot.error = True
                                continue


	if len(static.t_parsed) > datemask.sum():
		static.t_parsed = static.t_parsed[datemask]

	if not plot.error:
		for fun, plev in plot.requires_diagnostic:
			fun(plot, data, plev, static)


import time
#
#plotpathBackup = conf.plotpath
#conf.plotpath = "/home/chriswei/Figures/" 
for tidx, date in zip(range(len(static.t)), static.t_parsed):
	data_inst = {}
	for q in data:
		data_inst[q] = data[q][tidx]
	
	for plot in plots:
		plot.plot(data_inst, static, forecast, date)
		plt.close()
		
		# Temporarily delaying the plotting, to hopefully avoid random and obscure Permission denied errors.
		#time.sleep(0.5)

#conf.plotpath = plotpathBackup
# the end
