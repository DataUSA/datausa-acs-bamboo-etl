import requests
import numpy as np
import pandas as pd

from bamboo_lib.logger import logger
from acs.static import LIST_STATE, FIPS_CODE

def read_by_zone(year, geo, estimate, apis, api_key):
    if geo in ['us', 'state', 'county', 'place', 'metropolitan statistical area/micropolitan statistical area', 'congressional district', 'zip code tabulation area', 'public use microdata area']:   
        
        if geo in ['us', 'state', 'metropolitan statistical area/micropolitan statistical area', 'zip code tabulation area']: 
            df_all = pd.DataFrame({geo: []})
            merge = [geo]
        else: 
            df_all = pd.DataFrame({'state':[], geo: []})
            merge = ['state', geo]

        for api in apis:
            url = api[0].format(year, estimate, geo, api_key)
            logger.info("Downloading {}: {} from API...".format(year, geo))
            r = requests.get(url)
            content = r.json()
            
            df = pd.DataFrame(content[1::], columns=content[0])
            df_all = pd.merge(df, df_all, on=merge, how='outer') 

    else:
        df_all = pd.DataFrame()
        merge = ['state', 'county', geo]
        
        for i in LIST_STATE:
            df = pd.DataFrame({'state':[], 'county':[], geo: []})
            for api in apis:
                url = api[1].format(year, estimate, geo, api_key, i)
                logger.info("Downloading {}: {} ({}) from API...".format(year, geo, i))
                
                r = requests.get(url)
                content = r.json()
                
                df_geo = pd.DataFrame(content[1::], columns=content[0])
                df = pd.merge(df_geo, df, on=merge, how='outer') 
            
            df_all = df_all.append(df).reset_index(drop=True)

    return df_all