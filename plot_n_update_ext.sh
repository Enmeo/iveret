#!/bin/bash

# Setup some paths
basepath='/home/ubuntu/sw/vaerkart'
logpath='/home/ubuntu/log'
plotstat="$logpath/status"

fc=`python3 $basepath/current_ext_fc.py`
fcpath="/share/base/ecmwf_ext/$fc"

# Clean up old forecasts
$basepath/cleanup_ec_ext.sh

# Wait for all of these files to be present before starting the plotting
lastfiles="$fcpath/ec.ens.$fc.sfc.vinwvt.nc"

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

# Do the plotting first
python3 $basepath/plot_forecast_ext2.py sfc > $logpath/web_plot_ec_ext_sfc_out.log 2> $logpath/web_plot_ec_ext_sfc_err.log

# Mark the plotting as finished (required for rendering the correct websites)
echo $fc > $plotstat/ecmwf_ext


# Clean-up old plots
echo "Cleaning up old plots."
python3 $basepath/cleanup.py

# the end
