#!/usr/bin/env python
# -*- encoding: utf-8

STATUSFILE = '/home/ubuntu/log/status/KH_position.pickle'

import pickle
import json



def update_KH_position(lat, lon):
    f = open(STATUSFILE, 'wb')
    pickle.dump({'lat': lat, 'lon': lon}, f)
    f.close()

    print('Updated position pickle.')

    return


def get_KH_position():
    f = open(STATUSFILE, 'rb')
    dat = pickle.load(f)
    f.close()

    return dat['lat'], dat['lon']


if __name__ == '__main__':
    URL = 'http://vessel.npolar.io:8443/?token=qwertyuiop&mmsi=257275000'

    import requests as req

    resp = req.get(URL)
    dat = json.loads(resp.text)

    lon, lat = dat['geometry']['coordinates']
    update_KH_position(lat, lon)


# C'est le fin
