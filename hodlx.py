import json
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import requests
import time

NOW = time.strftime("%Y.%m.%d-%H:%M")
DATA_LOCATION = os.path.join(os.path.expanduser('~'), 'projects/hodlx/')
CMC_API_BASE = 'https://api.coinmarketcap.com/v2/'

def make_get_request(url, return_df=False):
    """Makes get request to specified url. Returns json or DataFrame object.
    """
    r = requests.get(url)
    if (r.ok):
        data = json.loads(r.content)
        if return_df:
            data = pd.DataFrame(data)
            if len(data.index) == 0:
                return None
    else:
        raise ValueError("Unable to fetch from {}!".format(url))
    return data

def fetch_cmc_ranking():
    """Fetches global marketcap data from coinmarketcap.com or disk. Defaults to all coins if n_coins not specified.
    """
    file_name = "cmc_ranking_{}.csv".format(NOW)
    file_path = os.path.join(DATA_LOCATION , file_name)

    if os.path.isfile(file_path):
        cmc_df = pd.read_csv(file_path, index_col=0)
    else:
        api_url = CMC_API_BASE + 'ticker/'
        cmc_dict = make_get_request(api_url)
        cmc_df = pd.DataFrame([value for value in cmc_dict['data'].values()])
        cmc_df.to_csv(file_path)
    return cmc_df
