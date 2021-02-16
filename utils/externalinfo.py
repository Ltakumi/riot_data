import requests
import json
import time
import random

path2patches = 'https://raw.githubusercontent.com/CommunityDragon/Data/master/patches.json'

def request_patch(ntries):

    error_code = []
    for i in range(ntries):
        resp = requests.get(path2patches)
        if resp.status_code == 200:
            return json.loads(resp.content.decode('utf-8'))
        else:
            error_code.append(resp.status_code )
            time.sleep(random.randint(0, 5))
    print('Error fetching patch informations', error_code)
    return None


def get_timestamped_patches(region, patches=None, ntries=10, unit='s'):

    all_patches = request_patch(ntries)

    # we add endtime
    res = {}
    for i, patch in enumerate(all_patches['patches'][:-1]):
        if patches is None or patch['name'] in patches:
            start = patch['start']+all_patches['shifts'][region.upper()]
            end = all_patches['patches'][i+1]['start']+all_patches['shifts'][region.upper()]
            res[patch['name']] = [start, end]

    # last patch
    if patches is None or all_patches['patches'][-1]['name']  in patches:
        start = all_patches['patches'][-1]['start']+all_patches['shifts'][region.upper()]
        res[all_patches['patches'][-1]['name']] = [start, int(time.time())]

    # base is s, riot sometimes uses ms
    if unit=='ms':
        for i in res:
            res[i][0], res[i][1] = 1000*res[i][0], 1000*res[i][1]

    return res
