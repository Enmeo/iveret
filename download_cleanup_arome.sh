#!/bin/bash

dest='/share/base/metno'
cd $dest

# Clean-up old forecasts: Older than 10 hours = 600 minutes
if [[ `pwd` = *"share"* ]]; then 
	find . -mmin +600 -delete
else
	echo "Skipping cleaning, wrong working directory!"
fi

time=`python3 /home/ubuntu/sw/vaerkart/current_fc_arome.py`
mkdir -p $dest/$time
cd $dest/$time

# Arome forecasts
python3 /home/ubuntu/sw/vaerkart/download_arome.py
python3 /home/ubuntu/sw/vaerkart/download_arome_section.py


# C'est le fin
