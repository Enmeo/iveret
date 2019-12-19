#!/bin/bash

# Setup some paths
basepath='/home/ubuntu/sw/vaerkart'
logpath='/home/ubuntu/log'
plotstat="$logpath/status"

$basepath/download_cleanup_arome.sh > $logpath/web_download_no_out.log 2> $logpath/web_download_no_err.log 

# Do the plotting first
python3 $basepath/plot_forecast_arome_arctic.py > $logpath/web_plot_no_arctic_out.log 2> $logpath/web_plot_no_arctic_err.log &
python3 $basepath/plot_forecast_arome_section.py > $logpath/web_plot_no_sect_out.log 2> $logpath/web_plot_no_sect_err.log &
python3 $basepath/plot_forecast_arome.py > $logpath/web_plot_no_out.log 2> $logpath/web_plot_no_err.log

# Mark the plotting as finished
python3 $basepath/current_fc_arome.py > $plotstat/arome

# Then render the fitting websites
python3 $basepath/web/render_vaerkart_arome.py > $logpath/web_render_no_out.log 2> $logpath/web_render_no_err.log
python3 $basepath/web/render_vaerkart_arome_scandes.py > $logpath/web_render_no_scandes_out.log 2> $logpath/web_render_no_scandes_err.log
python3 $basepath/web/render_vaerkart_arome_arctic.py > $logpath/web_render_no_arctic_out.log 2> $logpath/web_render_no_arctic_err.log
python3 $basepath/web/render_vaerkart_arome_we60.py > $logpath/web_render_no_we60_out.log 2> $logpath/web_render_no_we60_err.log
python3 $basepath/web/publoop.py  > $logpath/publoop_out.log 2> $logpath/publoo_err.log

# Clean-up old plots
python3 $basepath/cleanup.py

# the end
