#!/bin/bash

# Setup some paths
basepath='/Data/gfi/users/csp001/forecasts'
logpath='/work/csp001/log'

# Make the scripts find dynlib and django and the matplotlib config
export PYTHONPATH="$PYTHONPATH:/Data/gfi/users/local/lib/python2.7/site-packages"
export MPLCONFIGDIR="$basepath/mpl_config"

# Do the plotting first
python $basepath/plot_forecast.py > $logpath/plot_out 2> $logpath/plot_err

# Then render the fitting website
python $basepath/web/render_vaerkart.py > $logpath/render_out 2> $logpath/render_err
python $basepath/web/render_vaerkart_npolar.py > $logpath/render_out2 2> $logpath/render_err2

# Clean-up old plots
find $basepath/web/plots -ctime +13 -delete

# the end
