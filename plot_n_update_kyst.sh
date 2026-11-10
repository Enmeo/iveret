#!/bin/bash

# Setup some paths
basepath='/home/ubuntu/sw/vaerkart'
logpath='/home/ubuntu/log'

$basepath/download_cleanup_kyst.sh > $logpath/web_download_kyst_out.log 2> $logpath/web_download_kyst_err.log 

# Do the plotting first
python3 $basepath/plot_forecast_kyst2.py > $logpath/web_plot_kyst_out.log 2> $logpath/web_plot_kyst_err.log

# Clean-up old plots
python3 $basepath/cleanup.py

# the end
