from datetime import datetime
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
    """Makes get request to specified url. Returns json or DataFrame object."""
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

def fetch_cmc_ranking(save=False, quote='USD', limit=100):
    """Fetches global marketcap data from coinmarketcap.com or disk."""
    file_path = os.path.join(DATA_LOCATION ,"cmc_ranking.csv")

    try:
        cmc_df = pd.read_csv(file_path, index_col=0)
    except FileNotFoundError:
        api_url = CMC_API_BASE + 'ticker/?limit={}'.format(limit)
        cmc_raw = make_get_request(api_url)
        
        # metadata = cmc_raw['metadata']
        # cmc_date = datetime.fromtimestamp(metadata['timestamp'])

        cmc_data = []
        for key, val in cmc_raw['data'].items():
            quotes = val.pop('quotes')[quote]
            cmc_data.append({**val, **quotes})
        cmc_df = pd.DataFrame(cmc_data)
        if save:
            cmc_df.to_csv(file_path)
    
    return cmc_df
