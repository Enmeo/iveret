#!/bin/bash

dest='/share/base/gfs'
time=`python3 /home/ubuntu/sw/vaerkart/current_fc_gfs.py`

baseurl='http://www.ftp.ncep.noaa.gov/data/nccf/com/gfs/prod'
hour=${time:8}
cd $dest

for lead in `seq -f '%03g' 0 3 72`; do
	wget $baseurl/gfs.$time/gfs.t${hour}z.pgrb2.0p25.f$lead
done
for lead in `seq -f '%03g' 78 6 240`; do
	wget $baseurl/gfs.$time/gfs.t${hour}z.pgrb2.0p25.f$lead
done

# Clean-up old forecasts: Older than 22 hours = 1320 minutes
if [[ `pwd` = *"share"* ]]; then 
	find . -mmin +1320 -delete
else
	echo "Skipping cleaning, wrong working directory!"
fi

# C'est le fin
