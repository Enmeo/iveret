#!/bin/bash

dest='/share/base/metno'
time=`python3 /home/ubuntu/sw/vaerkart/current_fc_arome.py`

mkdir -p $dest/$time
cd $dest/$time

# Arome forecasts
python3 /home/ubuntu/sw/vaerkart/download_arome.py
python3 /home/ubuntu/sw/vaerkart/download_arome_section.py
python3 /home/ubuntu/sw/vaerkart/download_arome_arctic_add.py

cd $dest

# Clean-up old forecasts: Older than 22 hours = 1320 minutes
if [[ `pwd` = *"share"* ]]; then 
	find . -mmin +1320 -delete
else
	echo "Skipping cleaning, wrong working directory!"
fi

# C'est le fin
