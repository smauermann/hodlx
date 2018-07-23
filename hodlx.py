from datetime import datetime
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import requests
import time

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
        
        cmc_data = []
        for key, val in cmc_raw['data'].items():
            quotes = val.pop('quotes')[quote]
            cmc_data.append({**val, **quotes})
        cmc_df = pd.DataFrame(cmc_data)
        if save:
            cmc_df.to_csv(file_path)
    
    return cmc_df.set_index('symbol', drop=True)

def save_weights(weights):
    file_path = os.path.join(DATA_LOCATION, "weights.csv")
    weights.to_csv(file_path)

def compute_weights(market_cap, weights=None, min_weight=None, max_weight=None, decimals=4):
    if weights is None:
        weights = market_cap / market_cap.sum()
    
    if max_weight is not None:
        all_weights_below_max = False
        while not all_weights_below_max:
            above_max = weights > max_weight
            at_max = weights == max_weight

            if np.any(above_max):
                below_max = np.logical_and(~above_max, ~at_max)
                sum_above_max = np.sum(weights[above_max] - max_weight)
                weights[above_max] = max_weight
                weights[below_max] += sum_above_max * market_cap[below_max] / market_cap[below_max].sum()
                
            else:
                all_weights_below_max = True
    
    if min_weight is not None:
        all_weights_above_min = False
        
        while not all_weights_above_min:
            below_min = weights < min_weight
            at_min = weights == min_weight
            
            if np.any(below_min):
                above_min = np.logical_and(~below_min, ~at_min)
                sum_below_min = np.sum(weights[below_min] - min_weight)
                weights[below_min] = min_weight
                weights[above_min] += sum_below_min * market_cap[above_min] / market_cap[above_min].sum()
            else:
                all_weights_above_min = True
    return weights.round(decimals)

def compute_modified_weights(market_cap, n=None):
    if n is not None and n <= len(market_cap):
        market_cap = market_cap[:n]
    market_cap_weights = market_cap / market_cap.sum()
    
    # complex scheme 4.5%/20%/50% capping method from MVIS
    large_weight_max = 0.2
    large_weight_min = 0.05
    large_weight_cum_max = 0.5
    small_weight_max = 0.045

    large_weights = market_cap_weights > small_weight_max
    if large_weights.sum() < 5:
        large_weights[:5] = True
    small_weights = ~large_weights

    market_cap_weights[large_weights] *= large_weight_cum_max / market_cap_weights[large_weights].sum()
    market_cap_weights[small_weights] *= large_weight_cum_max / market_cap_weights[small_weights].sum()
    
    # make sure large weights are in range 0.05 and 0.2
    market_cap_weights[large_weights] = compute_weights(market_cap[large_weights], 
                                                        weights=market_cap_weights[large_weights], 
                                                        min_weight=large_weight_min, 
                                                        max_weight=large_weight_max)
    market_cap_weights[small_weights] = compute_weights(market_cap[small_weights],
                                                        weights=market_cap_weights[small_weights], 
                                                        max_weight=small_weight_max)
    
    return market_cap_weights.sort_values(ascending=False)

if __name__ == '__main__':
    def example():
        cmc_ranking = fetch_cmc_ranking()
        mcap = cmc_ranking['market_cap']
        weights = compute_modified_weights(mcap, 20)
        print(weights)

