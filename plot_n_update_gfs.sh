#!/bin/bash

# Setup some paths
basepath='/home/ubuntu/sw/vaerkart'
logpath='/home/ubuntu/log'
plotstat="$logpath/status"

fc=`python3 $basepath/current_fc_gfs.py`

$basepath/download_cleanup_gfs.sh > $logpath/web_download_gfs_out.log 2> $logpath/web_download_gfs_err.log 

# Do the plotting first
python3 $basepath/plot_forecast_gfs2.py pv2 > $logpath/web_plot_gfs_pv2_out.log 2> $logpath/web_plot_gfs_pv2_err.log &
python3 $basepath/plot_forecast_gfs2.py sfc > $logpath/web_plot_gfs_sfc_out.log 2> $logpath/web_plot_gfs_sfc_err.log &
python3 $basepath/plot_forecast_gfs2.py plev > $logpath/web_plot_gfs_plev_out.log 2> $logpath/web_plot_gfs_plev_err.log

# Mark the plotting as finished
echo $fc > $plotstat/gfs

# Clean-up old plots
python3 $basepath/cleanup.py

# the end
