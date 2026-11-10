#!/usr/bin/env python3

import xarray as xr
import time

from current_fc_kyst import get_current_fc_kyst, DATEFMT

zlevs = {'sfc': 0}

qs = {
    'u_eastward': zlevs.keys(),
    'v_northward': zlevs.keys(),
    'temperature': zlevs.keys(),
    'salinity': zlevs.keys(),
}

forecast = get_current_fc_kyst()
date = forecast.strftime(DATEFMT)

print(f'Downloading the {date} forecasts.')

source_urls = {
    'fc0': f'https://thredds.met.no/thredds/dodsC/fou-hi/norkystv3_his_files/{forecast.year}/{forecast.month}/{forecast.day}/norkyst800_his_zdepth_{forecast.strftime(DATEFMT)}_m00_AN.nc',
    'fc1': f'https://thredds.met.no/thredds/dodsC/fou-hi/norkystv3_his_files/{forecast.year}/{forecast.month}/{forecast.day}/norkyst800_his_zdepth_latest_m00_FC_0001.nc',
    'fc2': f'https://thredds.met.no/thredds/dodsC/fou-hi/norkystv3_his_files/{forecast.year}/{forecast.month}/{forecast.day}/norkyst800_his_zdepth_latest_m00_FC_0002.nc',
    'fc3': f'https://thredds.met.no/thredds/dodsC/fou-hi/norkystv3_his_files/{forecast.year}/{forecast.month}/{forecast.day}/norkyst800_his_zdepth_latest_m00_FC_0003.nc',
    'fc4': f'https://thredds.met.no/thredds/dodsC/fou-hi/norkystv3_his_files/{forecast.year}/{forecast.month}/{forecast.day}/norkyst800_his_zdepth_latest_m00_FC_0004.nc',
    'fc5': f'https://thredds.met.no/thredds/dodsC/fou-hi/norkystv3_his_files/{forecast.year}/{forecast.month}/{forecast.day}/norkyst800_his_zdepth_latest_m00_FC_0005.nc',
}

if __name__ == '__main__':
    for fcname, url_base in source_urls.items():
        yslc = '0:1:1147'
        xslc = '0:1:2746'
        if fcname == 'fc5':
            tslc = '0:3:0'
        else:
            tslc = '0:3:23'

        for q, levs in qs.items():
            for lev, idx in zlevs.items():
                url = url_base
                time.sleep(1.5)

                pslc = f'{idx}:1:{idx}'
            
                # Coordinates
                url += f'?time[{tslc}]'
                url += f',Y[{yslc}]'
                url += f',X[{xslc}]'
                url += f',projection_stere'
                url += f',lon[{yslc}][{xslc}]'
                url += f',lat[{yslc}][{xslc}]'
                
                # The actual data
                url += f',{q}[{tslc}]'
                url += f'[{pslc}]'
                url += f'[{yslc}][{xslc}]'

                ds = xr.open_dataset(url, engine='netcdf4')
                ds.to_netcdf(f'kyst_{fcname}.{date}.{lev}.{q}.nc')


# C'est le fin
