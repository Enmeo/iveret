#!/bin/bash

# Setup some paths
basepath='/home/ubuntu/sw/vaerkart'
logpath='/home/ubuntu/log'
plotstat="$logpath/status"

# Init time of this run; determined once, as plotting can last into the next window
fc=`python3 $basepath/current_fc_dmi.py`

$basepath/download_cleanup_dmi.sh > $logpath/web_download_dmi_out.log 2> $logpath/web_download_dmi_err.log 

# Do the plotting first
python3 $basepath/plot_forecast_dmi2.py > $logpath/web_plot_dmi_out.log 2> $logpath/web_plot_dmi_err.log

# Mark the plotting as finished
echo $fc > $plotstat/dmi
python3 $basepath/write_status.py dmi $fc > $logpath/web_status_dmi_out.log 2> $logpath/web_status_dmi_err.log

# Clean-up old plots
python3 $basepath/cleanup.py

# the end
