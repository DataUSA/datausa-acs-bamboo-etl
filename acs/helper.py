import requests
import numpy as np
import pandas as pd
 
from bamboo_lib.logger import logger
from functools import lru_cache
from acs.static import LIST_STATE, FIPS_CODE, LIST_SCHOOL_DISTRICT, SCHOOL_DISTRICT_PSEUDO

@lru_cache(maxsize=1000)
def get_url(url):
    return requests.get(url)

def select_geos(params, default):
    # --geo=school_district loads only school districts (ACS 5-year only)
    if params.get('geo') == 'school_district':
        if params.get('estimate') != '5':
            raise ValueError('School districts are only loaded for the ACS 5-year estimate')
        return LIST_SCHOOL_DISTRICT
    return default

def read_by_zone(year, geo, estimate, apis, api_key):
    if geo in ['us', 'state', 'county', 'place', 'metropolitan statistical area/micropolitan statistical area', 'congressional district', 'zip code tabulation area', 'public use microdata area'] + LIST_SCHOOL_DISTRICT:
        url = apis[0].format(year, estimate, geo, api_key)
        logger.info("Downloading {}: {} from API...".format(year, geo))
        
        r = get_url(url)
        content = r.json()
        
        df = pd.DataFrame(content[1::], columns=content[0])
    
    else:
        df = pd.DataFrame()
        print("aqui")
        
        for i in LIST_STATE:
            url = apis[1].format(year, estimate, geo, api_key, i)
            
            logger.info("Downloading {}: {} ({}) from API...".format(year, geo, i))
            
            r = get_url(url)
            content = r.json()
            
            df_tract = pd.DataFrame(content[1::], columns=content[0])
            df = df.append(df_tract).reset_index(drop=True)
    return df


def create_geoid_in_df(df, geo):
    if geo in LIST_SCHOOL_DISTRICT:
        # Pseudo-districts have no member in the School District dimension
        df = df[~df[geo].isin(SCHOOL_DISTRICT_PSEUDO)].reset_index(drop=True)

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


def read_file(name):
    df = pd.read_csv(name)[1::]
    return df

def read_multiple_files(table, list_file):
    df_all = pd.DataFrame({'GEO_ID': [], 'NAME': []})

    for i in list_file:
        name = table + '_{}_2014.csv'.format(i)
        df = pd.read_csv(name)[1::]
        df_all = pd.merge(df_all, df, on=['GEO_ID', 'NAME'], how='outer')

    return df_all

def empty_str_replace(string):
    try:
        return float(string)
    except ValueError:
        return np.nan
