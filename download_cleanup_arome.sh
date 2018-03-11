#!/bin/bash

dest='/share/base/metno'
time=`python3 /home/ubuntu/sw/vaerkart/current_fc_arome.py`
cd $dest

# Arome forecasts
baseurl='http://thredds.met.no/thredds/fileServer/meps25files'
for file in meps_det_pp_2_5km meps_det_vc_2_5km; do
	wget $baseurl/${file}_$time.nc
done

# Arome Arctic forecasts
baseurl='http://thredds.met.no/thredds/fileServer/aromearcticlatest'
for file in arome_arctic_sfx_2_5km arome_arctic_pp_2_5km; do
	wget $baseurl/${file}_$time.nc
done


# Clean-up old forecasts: Older than 22 hours = 1320 minutes
if [[ `pwd` = *"share"* ]]; then 
	find . -mmin +1320 -delete
else
	echo "Skipping cleaning, wrong working directory!"
fi

# C'est le fin
