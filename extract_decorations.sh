#!/bin/bash

plotdomain="snorway"
plotname="clba_msl"
ipath="/share/web/plots/$plotdomain/$plotname/no"
#opath="/share/web/static/deco"
opath="."

# Aspect 2:1; for cross sections
#geometry="103x460+921+0"

# Aspect 3:2; for ec_for, no_kyst_lofotenbasin
#geometry="147x720+1080+0"

# Aspect 1:1; for ec_for_npolar, ec_for_spolar and no_for, no_kyst, no_kyst_vestland, no_kyst_bergen, no_kyst_lofoten
geometry="130x960+960+0"

# Aspect about 5:4; for no_for_arctic
#geometry="102x956+750+0"

# Aspect about 9:8; for ec_for_scandies, no_for_full, no_kyst_full
#geometry="112x927+825+0"

# Extract the init date from the last changed file 
last_img=`ls -tr $ipath/* | tail -n 1`
date=${last_img: -29:10}
echo "Using forecast plots from $date to extract decorators."

# Extract colorbars
convert -crop ${geometry}\! $last_img $opath/cbar_${plotdomain}_${plotname}.png

# the end
