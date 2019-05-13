#!/bin/bash

dest='/share/base/metno'
time=`python3 /home/ubuntu/sw/vaerkart/current_fc_topaz.py`
cd $dest

# Arome forecasts
baseurl='https://thredds.met.no/thredds/dodsC/topaz'
wget -O topaz_fc_$time.nc "$baseurl/dataset-topaz4-arc-unmasked-be?stereographic,longitude[0:1:0][0:1:0],latitude[0:1:0][0:1:0],time[0:1:41],temperature[0:1:0][0:1:0][0:1:0][0:1:0],salinity[0:1:0][0:1:0][0:1:0][0:1:0],u[0:1:0][0:1:0][0:1:0][0:1:0],v[0:1:0][0:1:0][0:1:0][0:1:0],ssh[0:1:0][0:1:0][0:1:0],fice[0:1:0][0:1:0][0:1:0]"

# Clean-up old forecasts: Older than 22 hours = 1320 minutes
if [[ `pwd` = *"share"* ]]; then 
	find . -mmin +1320 -delete
else
	echo "Skipping cleaning, wrong working directory!"
fi

# C'est le fin
