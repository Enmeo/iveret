#!/bin/bash

# Setup some paths
basepath='/home/ubuntu/sw/vaerkart'
logpath='/home/ubuntu/log'
plotstat="$logpath/status"

$basepath/download_cleanup_dmi.sh > $logpath/web_download_dmi_out.log 2> $logpath/web_download_dmi_err.log 

# Do the plotting first
python3 $basepath/plot_forecast_dmi2.py > $logpath/web_plot_dmi_out.log 2> $logpath/web_plot_dmi_err.log

# Mark the plotting as finished
python3 $basepath/current_fc_dmi.py > $plotstat/dmi

# Clean-up old plots
python3 $basepath/cleanup.py

# the end
