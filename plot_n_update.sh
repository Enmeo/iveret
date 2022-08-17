#!/bin/bash

# Setup some paths
basepath='/home/ubuntu/sw/vaerkart'
logpath='/home/ubuntu/log'
plotstat="$logpath/status"

fc=`python3 $basepath/current_fc.py`
fcpath="/share/base/ecmwf/$fc"

# Clean up old forecasts
$basepath/cleanup_ec.sh

# Wait for all of these files to be present before starting the plotting
lastfiles="$fcpath/ec.for-hr.$fc.700.t.nc $fcpath/ec.for.$fc.pt330.pv.nc $fcpath/ec.ens.$fc.sfc.msl.nc"

# Attempt for 2 hours in intervals of 5 mins
attempts=24
somethingmissing=true
while [ "$somethingmissing" = true ] && [ $attempts -gt 0 ]; do
	somethingmissing=false
	for lastfile in $lastfiles; do
		echo "Checking for $lastfile"
		if [ ! -f $lastfile ]; then
			somethingmissing=true
		fi
	done

	if [ "$somethingmissing" = true ]; then
		echo "Incomplete download, sleeping 10 Minutes and trying again. $attempts attempts remain."
		sleep 5m
		attempts=$((attempts-1))
	fi
done

if [ "$somethingmissing" = true ]; then
	echo "Incomplete download after 3h, giving up."
	exit -1
fi

# Update the position of Lehmkuhl if possible
python3 $basepath/update_lehmkuhl_position.py > $logpath/web_update_lehmkuhl_out.log 2> $logpath/web_update_lehmkuhl_err.log

# Do the plotting first
python3 $basepath/plot_forecast_eclocal2.py > $logpath/web_plot_ec_local_out.log 2> $logpath/web_plot_ec_local_err.log &
python3 $basepath/plot_forecast2.py isentropic > $logpath/web_plot_ec_isentropic_out.log 2> $logpath/web_plot_ec_isentropic_err.log &
python3 $basepath/plot_forecast2.py pv2 > $logpath/web_plot_ec_pv2_out.log 2> $logpath/web_plot_ec_pv2_err.log &
python3 $basepath/plot_forecast2.py sfc > $logpath/web_plot_ec_sfc_out.log 2> $logpath/web_plot_ec_sfc_err.log &
python3 $basepath/plot_forecast2.py ens > $logpath/web_plot_ec_ens_out.log 2> $logpath/web_plot_ec_ens_err.log &
python3 $basepath/plot_forecast2.py plev > $logpath/web_plot_ec_plev_out.log 2> $logpath/web_plot_ec_plev_err.log
python3 $basepath/plot_forecast_meteograms.py > $logpath/web_plot_ec_meteograms_out.log 2> $logpath/web_plot_ec_meteograms_err.log &

# Mark the plotting as finished
echo $fc > $plotstat/ecmwf

# Then render the fitting website
python3 $basepath/web/render_vaerkart_natl.py > $logpath/web_render_ec_natl_out.log 2> $logpath/web_render_ec_natl_err.log
python3 $basepath/web/render_vaerkart_meteograms.py > $logpath/web_render_ec_meteograms_out.log 2> $logpath/web_render_ec_meteograms_err.log
python3 $basepath/web/publoop.py  > $logpath/publoop_out.log 2> $logpath/publoop_err.log
python3 $basepath/web2/vue_page.py  > $logpath/vuepage_out.log 2> $logpath/vuepage_err.log

# Clean-up old plots
python3 $basepath/cleanup.py

# the end
