#!/bin/bash

download_single () {
	file=$1
	minsize=$2
	sleep_=10
	for i in {1..5}; do
		if [ -f "$file" ]; then
			size=`stat -c%s "$file"`
			if [ "$size" -ge "$minsize" ]; then
				break
			fi
		fi

		if [ $i -gt 1 ]; then
			echo "Retrying download, attempt ${i}, waiting ${sleep_}s."
			sleep $sleep_
			sleep_=$(( 2 * $sleep_ ))
		fi

		wget "${baseurl}/${file}?api-key=${API_KEY}" -O $file
	done
}

dest='/share/base/dmi2'
time=`python3 /home/ubuntu/sw/vaerkart/current_fc_dmi.py`

# Clean-up old forecasts: Older than 10 hours = 600 minutes
cd $dest
if [[ `pwd` = *"share"* ]]; then 
	find . -mmin +600 -delete
else
	echo "Skipping cleaning, wrong working directory!"
fi

source /home/ubuntu/sw/vaerkart/.dmi_api_key
baseurl='https://dmigw.govcloud.dk/v1/forecastdata/download'

timestr=`date -d $time +"%Y%m%d%H"`
mkdir -p $dest/$timestr
cd $dest/$timestr

init=`date -d $time +"%Y-%m-%dT%H%M%SZ"`
for filetype in PL SF; do
	if [ "$filetype" == PL ]; then
		minsize=320000000
	else
		minsize=420000000 # 5350000000 if not init
	fi

	for hour in {0..60..3}; do
		valid=`date -d "$time + $hour hours" +"%Y-%m-%dT%H%M%SZ"`
		file="HARMONIE_DINI_${filetype}_${init}_${valid}.grib"
		download_single $file $minsize
	done
done


# C'est le fin
