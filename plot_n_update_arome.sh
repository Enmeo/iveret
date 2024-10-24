#!/bin/bash

# Setup some paths
basepath='/home/ubuntu/sw/vaerkart'
logpath='/home/ubuntu/log'
plotstat="$logpath/status"

$basepath/download_cleanup_arome.sh > $logpath/web_download_no_out.log 2> $logpath/web_download_no_err.log 

# Do the plotting first
python3 $basepath/plot_forecast_arome_arctic2.py > $logpath/web_plot_no_arctic_out.log 2> $logpath/web_plot_no_arctic_err.log &
python3 $basepath/plot_forecast_arome_section.py > $logpath/web_plot_no_sect_out.log 2> $logpath/web_plot_no_sect_err.log &
python3 $basepath/plot_forecast_arome2.py > $logpath/web_plot_no_out.log 2> $logpath/web_plot_no_err.log

# Mark the plotting as finished
python3 $basepath/current_fc_arome.py > $plotstat/arome

# Then render the fitting websites
python3 $basepath/publoop.py  > $logpath/publoop_out.log 2> $logpath/publoo_err.log

# Clean-up old plots
python3 $basepath/cleanup.py

# the end
