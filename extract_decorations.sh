#!/bin/bash

ipath="./web/plots"
opath="./web/static/deco"

plotdomain="no_for_arctic"

# Aspect 3:2; for ec_for
#geometry="147x720+1080+0"

# Aspect 1:1; for ec_for_npolar, ec_for_spolar and no_for
#geometry="130x960+960+0"

# Aspect about 5:4; for ec_for_scandies, no_for_full, no_for_arctic
geometry="102x956+750+0"


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
