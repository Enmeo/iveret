#!/bin/bash

dest='/share/base/metno/kyst'
time=`python3 /home/ubuntu/sw/vaerkart/current_fc_kyst.py`
timeday=${time::-2}
cd $dest

# NorKyst 800 analysis and forecasts
baseurl='https://thredds.met.no/thredds/ncss/fou-hi/norkyst800m-1h'
wget -O norkyst_an_$time.sfc.nc "$baseurl/NorKyst-800m_ZDEPTHS_his.an.$time.nc?var=salinity&var=temperature&var=u&var=v&disableLLSubset=on&disableProjSubset=on&horizStride=1&temporal=all&timeStride=3&vertCoord=0&addLatLon=true"
wget -O norkyst_fc_$time.sfc.nc "$baseurl/NorKyst-800m_ZDEPTHS_his.fc.$time.nc?var=salinity&var=temperature&var=u&var=v&disableLLSubset=on&disableProjSubset=on&horizStride=1&temporal=all&timeStride=3&vertCoord=0&addLatLon=true"

#wget -O norkyst_an_$time.100m.nc "$baseurl/NorKyst-800m_ZDEPTHS_his.an.$time.nc?var=salinity&var=temperature&var=u&var=v&disableLLSubset=on&disableProjSubset=on&horizStride=1&temporal=all&timeStride=3&vertCoord=100&addLatLon=true"
#wget -O norkyst_fc_$time.100m.nc "$baseurl/NorKyst-800m_ZDEPTHS_his.fc.$time.nc?var=salinity&var=temperature&var=u&var=v&disableLLSubset=on&disableProjSubset=on&horizStride=1&temporal=all&timeStride=3&vertCoord=100&addLatLon=true"

#wget -O norkyst_an_$time.300m.nc "$baseurl/NorKyst-800m_ZDEPTHS_his.an.$time.nc?var=salinity&var=temperature&var=u&var=v&disableLLSubset=on&disableProjSubset=on&horizStride=1&temporal=all&timeStride=3&vertCoord=300&addLatLon=true"
#wget -O norkyst_fc_$time.300m.nc "$baseurl/NorKyst-800m_ZDEPTHS_his.fc.$time.nc?var=salinity&var=temperature&var=u&var=v&disableLLSubset=on&disableProjSubset=on&horizStride=1&temporal=all&timeStride=3&vertCoord=300&addLatLon=true"

# ROMS Nordic 4km analysis and forecasts
baseurl='https://thredds.met.no/thredds/ncss/fou-hi/nordic4km-zdepths1h'
wget -O roms_nordic_an_$time.sfc.nc "$baseurl/roms_nordic4_ZDEPTHS_hr.an.$timeday.nc?var=salinity&var=temperature&var=u&var=v&disableLLSubset=on&disableProjSubset=on&horizStride=1&temporal=all&timeStride=3&vertCoord=0&addLatLon=true"
wget -O roms_nordic_fc_$time.sfc.nc "$baseurl/roms_nordic4_ZDEPTHS_hr.fc.$timeday.nc?var=salinity&var=temperature&var=u&var=v&disableLLSubset=on&disableProjSubset=on&horizStride=1&temporal=all&timeStride=3&vertCoord=0&addLatLon=true"

#wget -O roms_nordic_an_$time.100m.nc "$baseurl/roms_nordic4_ZDEPTHS_hr.an.$timeday.nc?var=salinity&var=temperature&var=u&var=v&disableLLSubset=on&disableProjSubset=on&horizStride=1&temporal=all&timeStride=3&vertCoord=100&addLatLon=true"
#wget -O roms_nordic_fc_$time.100m.nc "$baseurl/roms_nordic4_ZDEPTHS_hr.fc.$timeday.nc?var=salinity&var=temperature&var=u&var=v&disableLLSubset=on&disableProjSubset=on&horizStride=1&temporal=all&timeStride=3&vertCoord=100&addLatLon=true"

#wget -O roms_nordic_an_$time.300m.nc "$baseurl/roms_nordic4_ZDEPTHS_hr.an.$timeday.nc?var=salinity&var=temperature&var=u&var=v&disableLLSubset=on&disableProjSubset=on&horizStride=1&temporal=all&timeStride=3&vertCoord=300&addLatLon=true"
#wget -O roms_nordic_fc_$time.300m.nc "$baseurl/roms_nordic4_ZDEPTHS_hr.fc.$timeday.nc?var=salinity&var=temperature&var=u&var=v&disableLLSubset=on&disableProjSubset=on&horizStride=1&temporal=all&timeStride=3&vertCoord=300&addLatLon=true"


# Clean-up old forecasts: Older than 22 hours = 1320 minutes
if [[ `pwd` = *"share"* ]]; then 
	find . -mmin +1320 -delete
else
	echo "Skipping cleaning, wrong working directory!"
fi

# C'est le fin
