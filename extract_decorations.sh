#!/bin/bash

#ipath="/Data/gfi/users/csp001/forecasts/web/plots"
#opath="/Data/gfi/users/csp001/forecasts/web/static/deco"

ipath="/Home/siv22/csp001/work/iveret/vaerkart/web/plots"
opath="/Home/siv22/csp001/work/iveret/vaerkart/web/static/deco"

plotdomain="ec_for_npolar"

#geometry="120x720+1080+0"
geometry="107x960+960+0"

# Extract the init date from the last changed file 
last_img=`ls -tr $ipath/${plotdomain}* | tail -n 1`
date=${last_img: -29:10}
echo "Using forecast plots from $date to extract decorators."


for f in `ls $ipath/${plotdomain}_*_from_${date}_for_${date}.png`
do
	filename=${f##*/}
	tmp=${filename:${#plotdomain}+1}
	plotname=${tmp/_from_[0-9]*_for_[0-9]*.png/}
	echo "Processing $plotname"
	
	# Extract colorbars
	convert -crop ${geometry}\! $f $opath/cbar_${plotdomain}_${plotname}.png

done

# the end
