#!/bin/bash

# Setup some paths
basepath='/home/ubuntu/sw/vaerkart'
logpath='/home/ubuntu/log'

./download_cleanup_arome.sh

# Do the plotting first
python3 $basepath/plot_forecast_arome.py > $logpath/web_plot_no_out.log 2> $logpath/web_plot_no_err.log

# Then render the fitting website
python3 $basepath/web/render_vaerkart_arome.py > $logpath/web_render_no_out.log 2> $logpath/web_render_no_err.log
python3 $basepath/web/render_vaerkart_arome_scandies.py > $logpath/web_render_no_scandi_out.log 2> $logpath/web_render_no_scandi_err.log

# And then the same once more for the Arctic forecasts
python3 $basepath/plot_forecast_arome_arctic.py > $logpath/web_plot_no_arctic_out.log 2> $logpath/web_plot_no_arctic_err.log
python3 $basepath/web/render_vaerkart_arome_arctic.py > $logpath/web_render_no_arctic_out.log 2> $logpath/web_render_no_arctic_err.log

# Clean-up old plots
python3 cleanup.py

# the end
