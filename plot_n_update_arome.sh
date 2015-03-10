#!/bin/bash

# Setup some paths
basepath='/Data/gfi/metno/visualisation'
logpath='/Data/gfi/metno/log'

# Make the scripts find dynlib and django and the matplotlib config
export PYTHONPATH="$PYTHONPATH:/Data/gfi/users/local/lib/python2.7/site-packages"
export MPLCONFIGDIR="$basepath/mpl_config"

# Do the plotting first
python $basepath/plot_forecast_arome.py > $logpath/web_plot_no_out.log 2> $logpath/web_plot_no_err.log

# Then render the fitting website
python $basepath/web/render_vaerkart_arome.py > $logpath/web_render_no_out.log 2> $logpath/web_render_no_err.log

# Clean-up old plots
find $basepath/web/plots -ctime +13 -delete

# the end
