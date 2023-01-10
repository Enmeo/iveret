#!/bin/bash

dest='/share/base/ecmwf_ext'
cd $dest

# Clean-up old forecasts: Older than 60 hours = 3600 minutes
if [[ `pwd` = *"share"* ]]; then 
	sudo --user=ecmwf find . -mmin +3600 -delete
else
	echo "Skipping cleaning, wrong working directory!"
fi

# C'est le fin
