#!/bin/bash

# Setup some paths
basepath='/home/ubuntu/sw/vaerkart'
logpath='/home/ubuntu/log'
plotstat="$logpath/status"

# Clean up old forecasts
$basepath/cleanup_ec.sh

# Do the plotting first
python3 $basepath/plot_forecast_eclocal.py > $logpath/web_plot_ec_local_out.log 2> $logpath/web_plot_ec_local_err.log
python3 $basepath/plot_forecast.py isentropic > $logpath/web_plot_ec_isentropic_out.log 2> $logpath/web_plot_ec_isentropic_err.log &
python3 $basepath/plot_forecast.py pv2 sfc > $logpath/web_plot_ec_pv2sfc_out.log 2> $logpath/web_plot_ec_pv2sfc_err.log &
python3 $basepath/plot_forecast_slope.py > $logpath/web_plot_ec_slope_out.log 2> $logpath/web_plot_ec_slope_err.log &
python3 $basepath/plot_forecast.py plev > $logpath/web_plot_ec_plev_out.log 2> $logpath/web_plot_ec_plev_err.log

# Mark the plotting as finished
python3 $basepath/current_fc.py > $plotstat/ecmwf

# Then render the fitting website
python3 $basepath/web/render_vaerkart_scandes.py > $logpath/web_render_ec_scandes_out.log 2> $logpath/web_render_ec_scandes_err.log
python3 $basepath/web/render_vaerkart.py > $logpath/web_render_ec_out.log 2> $logpath/web_render_ec_err.log
python3 $basepath/web/render_vaerkart_npolar.py > $logpath/web_render_ec_npolar_out.log 2> $logpath/web_render_ec_npolar_err.log
python3 $basepath/web/render_vaerkart_spolar.py > $logpath/web_render_ec_spolar_out.log 2> $logpath/web_render_ec_spolar_err.log
python3 $basepath/web/publoop.py  > $logpath/publoop_out.log 2> $logpath/publoop_err.log

# Clean-up old plots
python3 $basepath/cleanup.py

# the end
