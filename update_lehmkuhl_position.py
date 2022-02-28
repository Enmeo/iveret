#!/usr/bin/env python
# -*- encoding: utf-8

STATUSFILE = '/home/ubuntu/log/status/lehmkuhl_position.pickle'

import pickle



def update_lehmkuhl_position(lat, lon):
    f = open(STATUSFILE, 'wb')
    pickle.dump({'lat': lat, 'lon': lon}, f)
    f.close()

    print('Updated position pickle.')

    return


def get_lehmkuhl_position():
    f = open(STATUSFILE, 'rb')
    dat = pickle.load(f)
    f.close()

    return dat['lat'], dat['lon']


if __name__ == '__main__':
    URL = 'https://lehmkuhl.no/forsiden/folg-skipet/'

    import requests as req
    import re

    lat_pattern = re.compile('lat: ([0-9.-]+),')
    lon_pattern = re.compile('lng: ([0-9.-]+) ')

    resp = req.get(URL)
    lats = lat_pattern.findall(resp.text)
    lons = lon_pattern.findall(resp.text)

    if len(lats) == 1 and len(lons) == 1:
        lat = float(lats[0])
        lon = float(lons[0])
        
        print(f'Found current position: {lat} degN, {lon} degE.')
        update_lehmkuhl_position(lat, lon)
    else:
        print(f'Found none/no unique position, but latitudes {lats}, and longitudes {lons}.')


# C'est le fin
