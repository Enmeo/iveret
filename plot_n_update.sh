#!/bin/bash

# Setup some paths
basepath='/Data/gfi/metno/visualisation'
logpath='/Data/gfi/metno/log'
# Make the scripts find dynlib and django and the matplotlib config
export PYTHONPATH="$PYTHONPATH:/Data/gfi/users/local/lib/python2.7/site-packages"
export MPLCONFIGDIR="$basepath/mpl_config"

# Do the plotting first
python $basepath/plot_forecast.py > $logpath/web_plot_ec_out.log 2> $logpath/web_plot_ec_err.log

# Then render the fitting website
python $basepath/web/render_vaerkart.py > $logpath/web_render_ec_out.log 2> $logpath/web_render_ec_err.log
python $basepath/web/render_vaerkart_npolar.py > $logpath/web_render_ec_npolar_out.log 2> $logpath/web_render_ec_npolar_err.log
python $basepath/web/render_vaerkart_spolar.py > $logpath/web_render_ec_spolar_out.log 2> $logpath/web_render_ec_spolar_err.log

# Clean-up old plots
find $basepath/web/plots -ctime +13 -delete

# the end
