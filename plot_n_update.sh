#!/bin/bash

# Setup some paths
basepath='/Data/gfi/metno/visualisation'
logpath='/Data/gfi/metno/log'
# Make the scripts find dynlib and django and the matplotlib config
source /Data/gfi/users/local/share/virtualenv/dynpie3/bin/activate
export MPLCONFIGDIR="$basepath/mpl_config"

# Do the plotting first
python $basepath/plot_forecast.py isentropes > $logpath/web_plot_ec_isentropes_out.log 2> $logpath/web_plot_ec_isentropes_err.log &
python $basepath/plot_forecast.py pv2 sfc > $logpath/web_plot_ec_pv2sfc_out.log 2> $logpath/web_plot_ec_pv2sfc_err.log &
python $basepath/plot_forecast.py plev > $logpath/web_plot_ec_plev_out.log 2> $logpath/web_plot_ec_plev_err.log

# Then render the fitting website
python $basepath/web/render_vaerkart.py > $logpath/web_render_ec_out.log 2> $logpath/web_render_ec_err.log
python $basepath/web/render_vaerkart_npolar.py > $logpath/web_render_ec_npolar_out.log 2> $logpath/web_render_ec_npolar_err.log
python $basepath/web/render_vaerkart_spolar.py > $logpath/web_render_ec_spolar_out.log 2> $logpath/web_render_ec_spolar_err.log
python $basepath/web/render_vaerkart_scandies.py > $logpath/web_render_ec_scandies_out.log 2> $logpath/web_render_ec_scandies_err.log

# Clean-up old plots
#find $basepath/web/plots -ctime +13 -delete
python $basemap/cleanup.py

# the end
