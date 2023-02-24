#!/usr/bin/env python
# -*- encoding: utf-8


from plotconfig import *
from settings.common2 import *

from current_fc import get_current_fc

import xarray as xr


requires = [
    ('700','u'), ('700', 'v'),
    ('sfc','viewvt'), ('sfc', 'vinwvt'),
]
qf = {'viewvt': 'viwve', 'vinwvt': 'viwvn'}

def get_single(fc_str, fc_str_prev, plev, q):
    fname = f'{fc_str}/ec.for.{fc_str}.{plev}.{q}'
    try:
        f, dat, static = metopen(fname, qf.get(q,q))
        dat = dat.squeeze()
    except Exception as e:
        print(type(e), e)
        dat = None
        static = None

    return dat, static


def save(dates, uts, vts, fname):
    coords = {
        'time': dates,
    }
    ncvars = {
        'u': (['time'], uts, {}),
        'v': (['time'], vts, {}),
    }
    ds = xr.Dataset(data_vars=ncvars, coords=coords, attrs={})
    ds.to_netcdf(f'/share/base/bimodal_extract/{fname}')

    return 


def extract_Alps(data):
    # Mean wind components at 700 hPa between 8-13 East, 46-47.5 North
    yslc = slice(85,89)
    xslc = slice(376,387)
    
    um = data['700','u'][:,yslc,xslc].mean(axis=2).mean(axis=1)
    vm = data['700','v'][:,yslc,xslc].mean(axis=2).mean(axis=1)

    return um, vm


def extract_NorthSea(data):
    # Moisture transport off the Norwegian west coast 3.5-4.5 East, 59-61 North
    yslc = slice(58,63)
    xslc = slice(367,370)

    um = data['sfc','viewvt'][:,yslc,xslc].mean(axis=2).mean(axis=1)
    vm = data['sfc','vinwvt'][:,yslc,xslc].mean(axis=2).mean(axis=1)

    return um, vm


if __name__ == '__main__':
    # Most recent available data
    forecast = get_current_fc()
    
    # Override
    forecast = dt(2023,2,23,0)
    
    print('Extract data from the %s forecasts' % forecast.strftime('%Y-%m-%d %H'))

    fc_str = forecast.strftime('%Y%m%d%H')
    fc_str_prev = (forecast-td(0.5)).strftime('%Y%m%d%H')
    conf.datapath.insert(1, '/share/base/ecmwf')
        
    data = {}
    for plev, q in requires:
        data[plev,q], grid = get_single(fc_str, fc_str_prev, plev, q)
    
    u, v = extract_Alps(data)
    save(grid.t_parsed, u, v, f'wind_Alps_{fc_str}.nc')

    u, v = extract_NorthSea(data)
    save(grid.t_parsed, u, v, f'moisture_transport_NorthSea_{fc_str}.nc')


    
# the end
