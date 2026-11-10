#!/bin/bash


dest='/share/base/metno_kyst'
cd $dest


# Clean-up old forecasts: Older than 22 hours = 1320 minutes
if [[ `pwd` = *"share"* ]]; then 
	find . -mmin +1320 -delete
else
	echo "Skipping cleaning, wrong working directory!"
fi


# C'est le fin
