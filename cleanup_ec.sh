#!/bin/bash

dest='/share/base/ecmwf'
cd $dest

# Clean-up old forecasts: Older than 46 hours = 2760 minutes
if [[ `pwd` = *"share"* ]]; then 
	sudo --user=ecmwf find . -mmin +2760 -delete
else
	echo "Skipping cleaning, wrong working directory!"
fi

# C'est le fin
