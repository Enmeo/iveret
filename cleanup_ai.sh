#!/bin/bash

dest='/share/base/ecmwf_ai'
cd $dest

# Clean-up old forecasts: Older than 34 hours = 2040 minutes
if [[ `pwd` = *"share"* ]]; then 
	sudo --user=ecmwf find . -mmin +2040 -delete
else
	echo "Skipping cleaning, wrong working directory!"
fi

# C'est le fin
