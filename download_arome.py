#!/usr/bin/env python3

import xarray as xr

from current_fc_arome import get_current_fc_arome, DATEFMT

plevs = {
    '700': 8, '850': 10, '925': 11,
}
sfclevs = {'sfc': 0}

qs = {
    'x_wind_pl': plevs.keys(),
    'y_wind_pl': plevs.keys(),
    'air_temperature_pl': plevs.keys(),
    'specific_humidity_pl': plevs.keys(),
    'turbulent_kinetic_energy_pl': plevs.keys(),
    'geopotential_pl': plevs.keys(),
    'precipitation_amount_acc': sfclevs.keys(),
    'x_wind_10m': sfclevs.keys(),
    'y_wind_10m': sfclevs.keys(),
    'air_temperature_2m': sfclevs.keys(),
    'air_pressure_at_sea_level': sfclevs.keys(),
    'relative_humidity_2m': sfclevs.keys(),
    'integral_of_surface_downward_latent_heat_evaporation_flux_wrt_time': sfclevs.keys(),
    'integral_of_surface_downward_latent_heat_sublimation_flux_wrt_time': sfclevs.keys(),
    'integral_of_surface_downward_sensible_heat_flux_wrt_time': sfclevs.keys(),
}

source_urls = {
    'arome': 'http://thredds.met.no/thredds/dodsC/meps25files/meps_det_extracted_2_5km_%s.nc',
    'arome_arctic': 'https://thredds.met.no/thredds/dodsC/aromearcticlatest/arome_arctic_extracted_2_5km_%s.nc',
}

xdims = {'arome': 888, 'arome_arctic': 738}
ydims = {'arome': 948, 'arome_arctic': 948}

forecast = get_current_fc_arome()
time = forecast.strftime(DATEFMT)
print(f'Downloading the {time} forecasts.')

if __name__ == '__main__':
    tslc = '0:3:66'
    for q, levs in qs.items():
        for lev in levs:
            if lev in plevs:
                idx = plevs[lev]
            else:
                idx = sfclevs[lev]
            pslc = f'{idx}:1:{idx}'
            
            for fcname, url in source_urls.items():
                yslc = '0:1:%d' % ydims[fcname]
                xslc = '0:1:%d' % xdims[fcname]

                # Coordinates
                url = url % time
                url += f'?time[{tslc}]'
                if lev in plevs:
                    url += f',pressure[{pslc}]'
                url += f',y[{yslc}]'
                url += f',x[{xslc}]'
                url += f',projection_lambert'
                url += f',longitude[{yslc}][{xslc}]'
                url += f',latitude[{yslc}][{xslc}]'
                
                # The actual data
                url += f',{q}[{tslc}]'
                url += f'[{pslc}]'
                url += f'[{yslc}][{xslc}]'

                ds = xr.open_dataset(url, engine='netcdf4')
                ds.to_netcdf(f'{fcname}.{time}.{lev}.{q}.nc')


# C'est le fin
