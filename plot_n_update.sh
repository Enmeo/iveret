#!/bin/bash

# Setup some paths
basepath='/home/ubuntu/sw/vaerkart'
logpath='/home/ubuntu/log'
plotstat="$logpath/status"

fc=`python3 $basepath/current_fc.py`
fcpath="/share/base/ecmwf/$fc"

# Clean up old forecasts
$basepath/cleanup_ec.sh
$basepath/cleanup_ai.sh

# Wait for all of these files to be present before starting the plotting
lastfiles="$fcpath/ec.for-hr.$fc.700.t.nc $fcpath/ec.for.$fc.pt330.pv.nc"

# Attempt for 2 hours in intervals of 5 mins
attempts=24
somethingmissing=true
while [ "$somethingmissing" = true ] && [ $attempts -gt 0 ]; do
	somethingmissing=false
	for lastfile in $lastfiles; do
		if [ ! -f $lastfile ]; then
			echo "Checking for ${lastfile}. Failed."
			somethingmissing=true
		else
			echo "Checking for ${lastfile}. Found."
		fi
	done

	if [ "$somethingmissing" = true ]; then
		echo "Incomplete download, sleeping 5 Minutes and trying again. $attempts attempts remain."
		sleep 5m
		attempts=$((attempts-1))
	fi
done

if [ "$somethingmissing" = true ]; then
	echo "Incomplete download after 2h, giving up."
	exit -1
fi

# Update the position of Kronprins Haakon if possible
python3 $basepath/update_KH_position.py > $logpath/web_update_KH_out.log 2> $logpath/web_update_KH_err.log

# Do the plotting first
python3 $basepath/plot_forecast_eclocal2.py > $logpath/web_plot_ec_local_out.log 2> $logpath/web_plot_ec_local_err.log &
python3 $basepath/plot_forecast2.py ai > $logpath/web_plot_ec_ai_out.log 2> $logpath/web_plot_ec_ai_err.log &
python3 $basepath/plot_forecast2.py isentropic > $logpath/web_plot_ec_isentropic_out.log 2> $logpath/web_plot_ec_isentropic_err.log &
python3 $basepath/plot_forecast2.py pv2 > $logpath/web_plot_ec_pv2_out.log 2> $logpath/web_plot_ec_pv2_err.log &
python3 $basepath/plot_forecast2.py sfc > $logpath/web_plot_ec_sfc_out.log 2> $logpath/web_plot_ec_sfc_err.log &
python3 $basepath/plot_forecast2.py plev > $logpath/web_plot_ec_plev_out.log 2> $logpath/web_plot_ec_plev_err.log

# Mark the plotting as finished (required for rendering the correct websites)
echo $fc > $plotstat/ecmwf

# Then render the fitting website
python3 $basepath/publoop.py  > $logpath/publoop_out.log 2> $logpath/publoop_err.log


# Wait for all of these files to be present before starting the plotting
lastfiles="$fcpath/ec.ens.$fc.sfc.msl.nc"

# Attempt for 1 hours in intervals of 5 mins
attempts=12
somethingmissing=true
while [ "$somethingmissing" = true ] && [ $attempts -gt 0 ]; do
	somethingmissing=false
	for lastfile in $lastfiles; do
		if [ ! -f $lastfile ]; then
			echo "Checking for ${lastfile}. Failed."
			somethingmissing=true
		else
			echo "Checking for ${lastfile}. Found."
		fi
	done

	if [ "$somethingmissing" = true ]; then
		echo "Incomplete download, sleeping 5 Minutes and trying again. $attempts attempts remain."
		sleep 5m
		attempts=$((attempts-1))
	fi
done

if [ "$somethingmissing" = true ]; then
	echo "Incomplete download after 1h, giving up."
	exit -1
fi

python3 $basepath/plot_forecast2.py ens > $logpath/web_plot_ec_ens_out.log 2> $logpath/web_plot_ec_ens_err.log &
python3 $basepath/extract_bimodal_for_natacha.py > $logpath/extract_for_natacha.log 2> $logpath/extract_for_natacha_err.log


# Wait for all of these files to be present before starting the plotting
lastfiles="$fcpath/ec.ens.$fc.sfc.meteogram.nc"

# Attempt for 1 hours in intervals of 5 mins
attempts=12
somethingmissing=true
while [ "$somethingmissing" = true ] && [ $attempts -gt 0 ]; do
	somethingmissing=false
	for lastfile in $lastfiles; do
		if [ ! -f $lastfile ]; then
			echo "Checking for ${lastfile}. Failed."
			somethingmissing=true
		else
			echo "Checking for ${lastfile}. Found."
		fi
	done

	if [ "$somethingmissing" = true ]; then
		echo "Incomplete download, sleeping 5 Minutes and trying again. $attempts attempts remain."
		sleep 5m
		attempts=$((attempts-1))
	fi
done

if [ "$somethingmissing" = true ]; then
	echo "Incomplete download after 1h, giving up."
	exit -1
fi

python3 $basepath/plot_forecast_meteograms.py > $logpath/web_plot_ec_meteograms_out.log 2> $logpath/web_plot_ec_meteograms_err.log &

# Clean-up old plots
echo "Cleaning up old plots."
python3 $basepath/cleanup.py

# the end
