#!/bin/bash

# Setup some paths
basepath='/home/ubuntu/sw/vaerkart'
logpath='/home/ubuntu/log'
plotstat="$logpath/status"

fc=`python3 $basepath/current_fc_gfs.py`
echo $fc

$basepath/download_cleanup_gfs.sh > $logpath/web_download_gfs_out.log 2> $logpath/web_download_gfs_err.log 

# Do the plotting first
python3 $basepath/plot_forecast_gfs.py $fc pv2 sfc > $logpath/web_plot_gfs_pv2sfc_out.log 2> $logpath/web_plot_gfs_pv2sfc_err.log &
python3 $basepath/plot_forecast_gfs.py $fc plev > $logpath/web_plot_gfs_plev_out.log 2> $logpath/web_plot_gfs_plev_err.log

# Mark the plotting as finished
echo $fc > $plotstat/gfs

# Then render the fitting website
python3 $basepath/web/render_vaerkart_gfs.py > $logpath/web_render_gfs_out.log 2> $logpath/web_render_gfs_err.log
python3 $basepath/web/render_vaerkart_gfs_npolar.py > $logpath/web_render_gfs_npolar_out.log 2> $logpath/web_render_gfs_npolar_err.log
python3 $basepath/web/render_vaerkart_gfs_spolar.py > $logpath/web_render_gfs_spolar_out.log 2> $logpath/web_render_gfs_spolar_err.log

# Clean-up old plots
python3 $basepath/cleanup.py

# the end
