#!/usr/bin/env python3

# Download some additiona stuff only available for the AROME Arctic forecasts

import xarray as xr

from current_fc_arome import get_current_fc_arome, DATEFMT

qs = ['SIC', 'SST', ]

source_urls = {
    'arome_arctic': 'https://thredds.met.no/thredds/dodsC/aromearcticlatest/arome_arctic_sfx_2_5km_%s.nc',
}

forecast = get_current_fc_arome()
time = forecast.strftime(DATEFMT)
print(f'Downloading the {time} forecasts.')

if __name__ == '__main__':
    tslc = '0:3:66'
    yslc = '0:1:948'
    xslc = '0:1:738'

    for q in qs:
        for fcname, url in source_urls.items():
            # Coordinates
            url = url % time
            url += f'?time[{tslc}]'
            url += f',y[{yslc}]'
            url += f',x[{xslc}]'
            url += f',projection_lambert'
            url += f',longitude[{yslc}][{xslc}]'
            url += f',latitude[{yslc}][{xslc}]'
            
            # The actual data
            url += f',{q}[{tslc}]'
            url += f'[{yslc}][{xslc}]'

            ds = xr.open_dataset(url, engine='netcdf4')
            ds.to_netcdf(f'{fcname}.{time}.sfc.{q}.nc')


# C'est le fin
