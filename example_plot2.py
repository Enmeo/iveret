#!/usr/bin/env python
# -*- encoding: utf-8
import numpy as np
from dynlib import *
from settings import *


plotname = 'ec_for' 		# Plot name, used only for creating the output file name

##### 850 temp, mslp ####
forecast = 2014052700 		# Forecast from

# Var 1
plev_1 = 850 			# Vertical level; must be either integer or string
q_1 = 't' 			# The variable; q stands for quantity

# Var 2
plev_2 = 'sfc'
q_2 = 'msl'

# Get the data 1
f1, dat1, static1 = metopen(conf.file_std % {'time': forecast, 'plev': plev_1, 'q': conf.qi[q_1]}, q_1)
f2, dat2, static2 = metopen(conf.file_std % {'time': forecast, 'plev': plev_2, 'q': conf.qi[q_2]}, q_2)

fi = plt.figure(figsize=(12.0,8.8), dpi=96)
fi.subplotpars.update(left=0.01, right=0.99, top=0.99, bottom=0.01)

# Define the configuration
i=24
overlays = [fig.map_overlay_dat(dat2[i]/100, static2, **conf.contour.merge('default', 
                                                                           contour_labels=True, 
                                                                           contour_labels_format='%1.0f',
                                                                           contour_labels_scale=range(960,1060,10), 
                                                                           linewidths=[1], 
                                                                           scale=range(960,1060,5) ) ), 
            fig.map_overlay_dat(dat1[i]-273.15, static1, **conf.contour.merge('default', 
                                                                              linewidths=[1], 
                                                                              linestyles='dashed',
                                                                              scale=range(0,2,2) ) ),
            ]

plotconf = conf.contourf.merge(q_1, 	# Get configuration for q, but override with the other arguments, like
                overlays=overlays,
                m=proj.NAmap, 		# Set a map projection
                coastcolor="gray",
                cmap=cm.t, # Set a colormap
		scale=range(-34,36,2),
                ticks=range(-34,36,2),
                ticklabels=range(-34,36,2),
                title='%s %s %s %s %s' % (q_1, plev_1, q_2, plev_2, static2.t_parsed[i].strftime('%Y%m%d%H')),
                show=False, 		# Do not display
                save='%s/%s_%s_%s_%s_%s_%s.png' % (conf.opath, plotname, q_1, plev_1, q_2, plev_2, static2.t_parsed[i].strftime('%Y%m%d%H')),
					# Rather save it, conf.opath is set in settings.py
)

fig.map_oro_dat(dat1[i]-273.15, static1, **plotconf)

 #that's it

##### 500 geopot, mslp #####
index= 'sequential_purple'
# Var 1
plev_1 = 500 			# Vertical level; must be either integer or string
q_1 = 'z' 			# The variable; q stands for quantity#

# Var 2
plev_2 = 'sfc'
q_2 = 'msl'

#Get the data
f1, dat1, static1 = metopen(conf.file_std % {'time': forecast, 'plev': plev_1, 'q': conf.qi[q_1]}, q_1)
f2, dat2, static2 = metopen(conf.file_std % {'time': forecast, 'plev': plev_2, 'q': conf.qi[q_2]}, q_2)


fi = plt.figure(figsize=(12.0,8.8), dpi=96)
fi.subplotpars.update(left=0.01, right=0.99, top=0.99, bottom=0.01)

# Define the configuration
i=24
overlays = [fig.map_overlay_dat(dat2[i]/100, static2, **conf.contour.merge('default', 
                                                                          contour_labels=True, 
                                                                           #colors='white', 
                                                                           linewidths=[1], 
                                                                           scale=range(960,1060,5) ) ),
         fig.map_overlay_dat(dat1[i]/98.0665, static2, **conf.contour.merge('default', 
                                                                           contour_labels=True, 
                                                                           colors='white',
                                                                           linewidths=[1],
                                                                           linestyles='dashed',
                                                                           scale=range(472,601,16) ) ),
          fig.map_overlay_dat(dat1[i]/98.0665, static2, **conf.contour.merge('default', 
                                                                           contour_labels=True, 
                                                                           colors='white',
                                                                           linewidths=[2],
                                                                           scale=range(552,554,2) ) ), 
           ]
plotconf = conf.contourf.merge(q_1, 	# Get configuration for q, but override with the other arguments, like
                overlays=overlays,
                m=proj.NAmap, 		# Set a map projection
                coastcolor='gray',
	#	cmap=cm.YlOrBr, # Set a colormap
                cmap=cm.z,
        	scale=range(476,604,4),
                ticks=range(476,604,4),
                ticklabels=range(476,604,4),
                title='%s %s %s %s %s' % (q_1, plev_1, q_2, plev_2, static2.t_parsed[i].strftime('%Y%m%d%H')),
                show=False, 		# Do not display
                save='%s/%s_%s_%s_%s_%s_%s_%s.png' % (conf.opath, plotname, q_1, plev_1, q_2, plev_2, static2.t_parsed[i].strftime('%Y%m%d%H'), index),
					# Rather save it, conf.opath is set in settings.py
)

fig.map_oro_dat(dat1[i]/98.0665, static1, **plotconf)

#### q #####

# Var 1
plev_1 = 850 			# Vertical level; must be either integer or string
q_1 = 'q' 			# The variable; q stands for quantity

#Var 2
plev_2 = 850
q_2 = 'u'

#Var 3
plev_3 = 850
q_3 = 'v'

#Get the data
f1, dat1, static1 = metopen(conf.file_std % {'time': forecast, 'plev': plev_1, 'q': conf.qi[q_1]}, q_1)
f2, dat2, static2 = metopen(conf.file_std % {'time': forecast, 'plev': plev_2, 'q': conf.qi[q_2]}, q_2)
f3, dat3, static3 = metopen(conf.file_std % {'time': forecast, 'plev': plev_3, 'q': conf.qi[q_3]}, q_3)

fi = plt.figure(figsize=(12.0,8.8), dpi=96)
fi.subplotpars.update(left=0.01, right=0.99, top=0.99, bottom=0.01)

# Define the configuration
i=1

fig.map_oro_barb(dat2[i], 
                 dat3[i], 
                 static2,
                 dat=dat1[i]*1000,
                 cmap=cm.q,
                 scale=np.arange(1,16,1),
                 ticks=np.arange(1,16,1),
                 q=q_2, 
                 m=proj.NAmap,
                 coastcolor='gray',
                 title='%s %s %s %s %s' % (q_1, q_2, q_3, plev_3, static3.t_parsed[i].strftime('%Y%m%d%H')),
                 show=False, 		# Do not display
                 save='%s/%s_%s_%s_%s_%s_%s.png' % (conf.opath, plotname,q_1, q_2, q_3, plev_3, static3.t_parsed[i].strftime('%Y%m%d%H')),
) 


### precip ####


# Var 1
plev_1 = 'sfc' 			# Vertical level; must be either integer or string
q_1 = 'lsp' 			# The variable; q stands for quantity

#Var 2
plev_2 = 'sfc'
q_2 = 'cp'

i=4
#Get the data
f1, dat1, static1 = metopen(conf.file_std % {'time': forecast, 'plev': plev_1, 'q': conf.qi[q_1]}, q_1)
f2, dat2, static2 = metopen(conf.file_std % {'time': forecast, 'plev': plev_2, 'q': conf.qi[q_2]}, q_2)

fi = plt.figure(figsize=(12.0,8.8), dpi=96)
fi.subplotpars.update(left=0.01, right=0.99, top=0.99, bottom=0.01)

if (i==0): 
    dat=dat1[i]+dat2[i]
else: 
    dat1_red=dat1[i]-dat1[i-1]
    dat2_red=dat2[i]-dat2[i-1]
    dat=dat1_red+dat2_red

s=[0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.4, 2.0, 3.0, 5.0, 7.0, 10.0, 14.0, 20.0, 30.0, 50.0]
st=[0,0.1, 0.2, 0.3, 0.5, 0.7, 1.0, 1.4, 2.0, 3.0, 5.0, 7.0, 10.0, 14.0, 20.0, 30.0, 50.0,70.0]
plotconf = conf.contourf.merge(q_1, 	# Get configuration for q, but override with the other arguments, like
                m=proj.NAmap, 		# Set a map projection
                coastcolor='gray',
		cmap=cm.prec_bl, # Set a colormap
                #cmap=cm.z,
                norm=mpl.colors.LogNorm(s),
                extend="neither",
                scale=s,
                ticks=s,
                ticklabels=s,
                title='%s %s' % ("10h-Precipitation", static2.t_parsed[i].strftime('%Y%m%d%H')),
                show=False, 		# Do not display
                save='%s/%s_%s_%s.png' % (conf.opath, plotname, "tot_prec", static2.t_parsed[i].strftime('%Y%m%d%H')),
       				# Rather save it, conf.opath is set in settings.py
)

fig.map_oro_dat(dat*1000, static1, **plotconf)


### PV wind pt=300 ###


# Var 1
plev_1 = 'pt300' 			# Vertical level; must be either integer or string
q_1 = 'pv' 			# The variable; q stands for quantity

#Var 2
plev_2 = 'pt300'
q_2 = 'u'

#Var 3
plev_3 = 'pt300'
q_3 = 'v'

#Get the data
f1, dat1, static1 = metopen(conf.file_std % {'time': forecast, 'plev': plev_1, 'q': conf.qi[q_1]}, q_1)
f2, dat2, static2 = metopen(conf.file_std % {'time': forecast, 'plev': plev_2, 'q': conf.qi[q_2]}, q_2)
f3, dat3, static3 = metopen(conf.file_std % {'time': forecast, 'plev': plev_3, 'q': conf.qi[q_3]}, q_3)

fi = plt.figure(figsize=(12.0,8.8), dpi=96)
fi.subplotpars.update(left=0.01, right=0.99, top=0.99, bottom=0.01)

## Define the configuration
i=1
overlays=[fig.map_overlay_dat(dat1[i]*10**6, static1, **conf.contour.merge('default', 
                                                                           contour_labels=True, 
                                                                           linewidths=[1.5],
                                                                           # linestyles='dashed',
                                                                           scale=range(2,3,1) ) ), 
            ]

s=[0, 1.0,  2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
st=[0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
fig.map_oro_barb(dat2[i], 
                 dat3[i], 
                 static2,
                 dat=dat1[i]*10**6,
                 overlays=overlays,
                 cmap=cm.pv_new,
                 norm=mpl.colors.BoundaryNorm(s, 256),
                 scale=s,
                 ticks=st,
                 q=q_2, 
                 m=proj.NAmap,
                 coastcolor='gray',
                 title='%s %s %s %s %s' % (q_1, q_2, q_3, plev_3, static3.t_parsed[i].strftime('%Y%m%d%H')),
                 show=False, 		# Do not display
                 save='%s/%s_%s_%s_%s_%s_%s.png' % (conf.opath, plotname,q_1, q_2, q_3, plev_3, static3.t_parsed[i].strftime('%Y%m%d%H')),
) 


##### theta and wind  on pv=2 surface ####


# Var 1
plev_1 = 'pv2000' 			# Vertical level; must be either integer or string
q_1 = 'pt' 			# The variable; q stands for quantity

#Var 2
plev_2 = 'pv2000'
q_2 = 'u'

#Var 3
plev_3 = 'pv2000'
q_3 = 'v'

#Get the data
f1, dat1, static1 = metopen(conf.file_std % {'time': forecast, 'plev': plev_1, 'q': conf.qi[q_1]}, q_1)
f2, dat2, static2 = metopen(conf.file_std % {'time': forecast, 'plev': plev_2, 'q': conf.qi[q_2]}, q_2)
f3, dat3, static3 = metopen(conf.file_std % {'time': forecast, 'plev': plev_3, 'q': conf.qi[q_3]}, q_3)

fi = plt.figure(figsize=(12.0,8.8), dpi=96)
fi.subplotpars.update(left=0.01, right=0.99, top=0.99, bottom=0.01)

## Define the configuration
i=1
overlays=[fig.map_overlay_dat(dat1[i]*10**6, static1, **conf.contour.merge('default', 
                                                                           contour_labels=True, 
                                                                           linewidths=[1],
                                                                           scale=range(2,3,1) ) ), 
            ]
fig.map_oro_barb(dat2[i], 
                 dat3[i], 
                 static2,
                 dat=dat1[i],
                 overlays=overlays,
                 cmap=cm.t,
                 scale=np.arange(270,385,5),
                 ticks=np.arange(270,385,5),
                 q=q_2, 
                 m=proj.NAmap,
                 coastcolor='gray',
                 title='%s %s %s %s %s' % (q_1, q_2, q_3, plev_3, static3.t_parsed[i].strftime('%Y%m%d%H')),
                 show=False, 		# Do not display
                 save='%s/%s_%s_%s_%s_%s_%s.png' % (conf.opath, plotname,q_1, q_2, q_3, plev_3, static3.t_parsed[i].strftime('%Y%m%d%H')),
) 


### total column water vapour ####

index="North_Atlantic"
# Var 1
plev_1 = 'sfc' 			# Vertical level; must be either integer or string
q_1 = 'tcwv' 			# The variable; q stands for quantity


i=4
#Get the data
f1, dat1, static1 = metopen(conf.file_std % {'time': forecast, 'plev': plev_1, 'q': conf.qi[q_1]}, q_1)

fi = plt.figure(figsize=(12.0,8.8), dpi=96)
fi.subplotpars.update(left=0.01, right=0.99, top=0.99, bottom=0.01)

s_glob=[3,6,9,12,15,18,21,24,27,30,35,40,45,50,55,60,65]
s_NA=range(0,42,2)
plotconf = conf.contourf.merge(q_1, 	# Get configuration for q, but override with the other arguments, like
                m=proj.NAmap, 		# Set a map projection
                coastcolor='gray',
		cmap=cm.q,
                scale=s_NA,           
                ticks=s_NA,
                ticklabels=s_NA,
                title='%s %s %s' % (q_1, static2.t_parsed[i].strftime('%Y%m%d%H'), index),
                show=False, 		# Do not display
                save='%s/%s_%s_%s_%s.png' % (conf.opath, plotname,q_1, index, static2.t_parsed[i].strftime('%Y%m%d%H')),
       				# Rather save it, conf.opath is set in settings.py
)

fig.map_oro_dat(dat1[i], static1, **plotconf)

### total cloud cover ####


# Var 1
plev_1 = 'sfc' 			# Vertical level; must be either integer or string
q_1 = 'tcc' 			# The variable; q stands for quantity


i=4
#Get the data
f1, dat1, static1 = metopen(conf.file_std % {'time': forecast, 'plev': plev_1, 'q': conf.qi[q_1]}, q_1)

fi = plt.figure(figsize=(12.0,8.8), dpi=96)
fi.subplotpars.update(left=0.01, right=0.99, top=0.99, bottom=0.01)

s=[0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0]
plotconf = conf.contourf.merge(q_1, 	# Get configuration for q, but override with the other arguments, like
                #m=proj.NAmap, 		# Set a map projection
                coastcolor='gray',
		cmap=cm.q_r, # Set a colormap
                scale=s,
                ticks=s,
                ticklabels=["0/8","1/8", "2/8", "3/8", "4/8", "5/8", "6/8", "7/8", "8/8"],
                title='%s %s' % (q_1, static2.t_parsed[i].strftime('%Y%m%d%H')),
                show=False, 		# Do not display
                save='%s/%s_%s_%s.png' % (conf.opath, plotname,q_1, static2.t_parsed[i].strftime('%Y%m%d%H')),
       				# Rather save it, conf.opath is set in settings.py
)

fig.map_oro_dat(dat1[i], static1, **plotconf)
