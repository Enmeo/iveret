#!/bin/bash

#ipath="/Data/gfi/users/csp001/forecasts/web/plots"
#opath="/Data/gfi/users/csp001/forecasts/web/static/deco"

ipath="/Home/siv22/csp001/work/iveret/vaerkart/web/plots"
opath="/Home/siv22/csp001/work/iveret/vaerkart/web/static/deco"


# Extract the init date from the last changed file 
last_img=`ls -tr $ipath | tail -n 1`
date=${last_img: -29:10}
echo "Using forecast plots from $date to extract decorators."


for f in `ls $ipath/ec_for_*_from_${date}_for_${date}.png`
do
	filename=${f##*/}
	tmp=${filename:7}
	plotname=${tmp/_from_[0-9]*_for_[0-9]*.png/}
	echo "Processing $plotname"
	
	# Extract colorbars
	convert -crop 120x720+1080+0\! $f $opath/cbar_${plotname}.png

done

# the end
