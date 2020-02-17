#!/usr/bin/env python3

import xarray as xr
import time

from current_fc_arome import get_current_fc_arome, DATEFMT

sections = {
    'arome': {
#        'W-E_58': '0:1:232',
        'W-E_60': '233:1:454',
#        'W-E_62': '455:1:787',
    }
}
sfclevs = {'sfc': 0}

qs = ['x_wind_ml', 'y_wind_ml','upward_air_velocity_ml',  'air_temperature_ml', 'specific_humidity_ml', 'turbulent_kinetic_energy_ml', ]

source_urls = {
    'arome': 'https://thredds.met.no/thredds/dodsC/mepslatest/meps_det_vc_2_5km_%s.ncml',
}

forecast = get_current_fc_arome()
date = forecast.strftime(DATEFMT)
print(f'Downloading the {date} forecasts.')

if __name__ == '__main__':
    tslc = '0:3:66'
    pslc = '0:1:64'
    yslc = '0:1:0'
    for fcname, url_base in source_urls.items():
        for secname, secdef in sections[fcname].items():
            xslc = secdef

            for q in qs:
                time.sleep(1.5)

                # Coordinates
                url = url_base % date
                url += f'?time[{tslc}]'
                url += f',y[{yslc}]'
                url += f',x[{xslc}]'
                url += f',ap[{pslc}]'
                url += f',b[{pslc}]'
                url += f',surface_air_pressure[{tslc}][0:1:0][{yslc}][{xslc}]'
                url += f',longitude[{yslc}][{xslc}]'
                url += f',latitude[{yslc}][{xslc}]'
                
                # The actual data
                url += f',{q}[{tslc}][{pslc}][{yslc}][{xslc}]'

                ds = xr.open_dataset(url, engine='netcdf4')
                ds.to_netcdf(f'{fcname}.{date}.sect.{secname}.{q}.nc')


# C'est le fin
