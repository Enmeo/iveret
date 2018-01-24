#!/bin/bash

# Setup some paths
basepath='/Data/gfi/metno/visualisation'
logpath='/Data/gfi/metno/log'
# Make the scripts find dynlib and django and the matplotlib config
source /Data/gfi/users/local/share/virtualenv/dynpie3/bin/activate
export MPLCONFIGDIR="$basepath/mpl_config"

# Do the plotting first
python $basepath/plot_forecast_eclocal.py > $logpath/web_plot_ec_local_out.log 2> $logpath/web_plot_ec_local_err.log &

# Then render the fitting website
python $basepath/web/render_vaerkart_scandies.py > $logpath/web_render_ec_scandies_out.log 2> $logpath/web_render_ec_scandies_err.log

# the end
