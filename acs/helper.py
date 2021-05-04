import requests
import numpy as np
import pandas as pd

from acs.static import LIST_STATE, FIPS_CODE

def read_by_zone(year, geo, estimate, apis):
    if geo != 'tract':
        url = apis[0].format(year, estimate, geo)
        
        r = requests.get(url)
        content = r.json()
        
        df = pd.DataFrame(content[1::], columns=content[0])
    else:
        df = pd.DataFrame()
        
        for i in LIST_STATE:
            url = apis[1].format(year, estimate, 'tract', i)
            
            r = requests.get(url)
            content = r.json()
            
            df_tract = pd.DataFrame(content[1::], columns=content[0])
            df = df.append(df_tract).reset_index(drop=True)
    return df

def create_geoid_in_df(df, geo):
    if geo == 'us':
        df['geoid'] = FIPS_CODE[geo]
    elif geo == 'state':
        df['geoid'] = df.apply(lambda x: FIPS_CODE[geo] + '{:02d}'.format(int(x['state'])), axis=1) 
    elif geo == 'county':
        df['geoid'] = df.apply(lambda x: FIPS_CODE[geo] + '{:02d}'.format(int(x['state'])) + '{:03d}'.format(int(x['county'])), axis=1)
    elif geo == 'metropolitan statistical area/micropolitan statistical area':
        df.rename(columns = {'metropolitan statistical area/micropolitan statistical area': 'msa'}, inplace=True)
        df['geoid'] = df.apply(lambda x: FIPS_CODE['msa'] + '{:05d}'.format(int(x['msa'])), axis=1)
    elif geo == 'tract':
        df['geoid'] = df.apply(lambda x: FIPS_CODE[geo] + '{:02d}'.format(int(x['state'])) + '{:03d}'.format(int(x['county'])) + '{:06d}'.format(int(x[geo])), axis=1)
    elif geo == 'congressional district':
        df['congressional district'] = df['congressional district'].replace('ZZ', 0)
        df['geoid'] = df.apply(lambda x: FIPS_CODE[geo] + '{:02d}'.format(int(x['state'])) + '{:02d}'.format(int(x['congressional district'])), axis=1)
    elif geo == 'zip code tabulation area':
        df['geoid'] = df.apply(lambda x: FIPS_CODE[geo] + '{:05d}'.format(int(x[geo])), axis=1)
    else:
        df['geoid'] = df.apply(lambda x: FIPS_CODE[geo] + '{:02d}'.format(int(x['state'])) + '{:05d}'.format(int(x[geo])), axis=1)
    return df