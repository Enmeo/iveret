#!/bin/bash

# Setup some paths
basepath='/home/ubuntu/sw/vaerkart'
logpath='/home/ubuntu/log'
plotstat="$logpath/status"

fc=`python3 $basepath/current_fc.py`
lastfile="/share/base/ecmwf/$fc/ec.for-NA.$fc.200.w.nc"

attempts=18
while [ ! -f $lastfile ] && [ $attempts -gt 0 ]; do
	echo "Incomplete download, sleeping 10 Minutes and trying again. $attempts attempts remain."
	sleep 10m
	attempts=$((attempts-1))
done

if [ ! -f $lastfile ]; then
	echo "Incomplete download after 3h, giving up."
	exit -1
fi

# Clean up old forecasts
$basepath/cleanup_ec.sh

# Do the plotting first
python3 $basepath/plot_forecast_eclocal.py > $logpath/web_plot_ec_local_out.log 2> $logpath/web_plot_ec_local_err.log &
python3 $basepath/plot_forecast.py isentropic > $logpath/web_plot_ec_isentropic_out.log 2> $logpath/web_plot_ec_isentropic_err.log &
python3 $basepath/plot_forecast.py pv2 sfc > $logpath/web_plot_ec_pv2sfc_out.log 2> $logpath/web_plot_ec_pv2sfc_err.log &
python3 $basepath/plot_forecast.py ens > $logpath/web_plot_ec_ens_out.log 2> $logpath/web_plot_ec_ens_err.log &
python3 $basepath/plot_forecast_slope.py > $logpath/web_plot_ec_slope_out.log 2> $logpath/web_plot_ec_slope_err.log &
python3 $basepath/plot_forecast_meteograms.py > $logpath/web_plot_ec_meteograms_out.log 2> $logpath/web_plot_ec_meteograms_err.log &
python3 $basepath/plot_forecast.py plev > $logpath/web_plot_ec_plev_out.log 2> $logpath/web_plot_ec_plev_err.log

# Mark the plotting as finished
echo $fc > $plotstat/ecmwf

# Then render the fitting website
python3 $basepath/web/render_vaerkart_scandes.py > $logpath/web_render_ec_scandes_out.log 2> $logpath/web_render_ec_scandes_err.log
python3 $basepath/web/render_vaerkart.py > $logpath/web_render_ec_out.log 2> $logpath/web_render_ec_err.log
python3 $basepath/web/render_vaerkart_npolar.py > $logpath/web_render_ec_npolar_out.log 2> $logpath/web_render_ec_npolar_err.log
python3 $basepath/web/render_vaerkart_spolar.py > $logpath/web_render_ec_spolar_out.log 2> $logpath/web_render_ec_spolar_err.log
python3 $basepath/web/render_vaerkart_natl.py > $logpath/web_render_ec_natl_out.log 2> $logpath/web_render_ec_natl_err.log
python3 $basepath/web/render_vaerkart_meteograms.py > $logpath/web_render_ec_meteograms_out.log 2> $logpath/web_render_ec_meteograms_err.log
python3 $basepath/web/publoop.py  > $logpath/publoop_out.log 2> $logpath/publoop_err.log
python3 $basepath/web2/vue_page.py  > $logpath/vuepage_out.log 2> $logpath/vuepage_err.log

# Clean-up old plots
python3 $basepath/cleanup.py

# the end
