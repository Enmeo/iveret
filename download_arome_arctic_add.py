#!/usr/bin/env python3

# Download some additiona stuff only available for the AROME Arctic forecasts

import xarray as xr

from current_fc_arome import get_current_fc_arome, DATEFMT


forecast = get_current_fc_arome()
time = forecast.strftime(DATEFMT)
print(f'Downloading the {time} forecasts.')


def download(qs, source_urls, add_z=False):
    tslc = '0:3:66'
    zslc = '0:1:0'
    yslc = '0:1:948'
    xslc = '0:1:738'

    for q in qs:
        for fcname, url in source_urls.items():
            # Coordinates
            url = url % time
            url += f'?time[{tslc}]'
            if add_z:
                 url += f',atmosphere_as_single_layer[{zslc}]'
            url += f',y[{yslc}]'
            url += f',x[{xslc}]'
            url += f',projection_lambert'
            url += f',longitude[{yslc}][{xslc}]'
            url += f',latitude[{yslc}][{xslc}]'
            
            # The actual data
            url += f',{q}[{tslc}]'
            if add_z:
                url += f'[{zslc}]'
            url += f'[{yslc}][{xslc}]'

            ds = xr.open_dataset(url, engine='netcdf4')
            if add_z:
                ds = ds.squeeze()
            ds.to_netcdf(f'{fcname}.{time}.sfc.{q}.nc')
    
    return


if __name__ == '__main__':
    qs = ['SIC', 'SST', ]
    source_urls = {
        'arome_arctic': 'https://thredds.met.no/thredds/dodsC/aromearcticlatest/arome_arctic_sfx_2_5km_%s.nc',
    }
    download(qs, source_urls)


    qs = ['cloud_base_altitude', ]
    source_urls = {
        'arome_arctic': 'https://thredds.met.no/thredds/dodsC/aromearcticlatest/arome_arctic_full_2_5km_%s.nc',
    }
    download(qs, source_urls, add_z=True)



# C'est le fin
