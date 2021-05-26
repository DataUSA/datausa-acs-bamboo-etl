import requests
import numpy as np
import pandas as pd
import os
import swifter

from bamboo_lib.connectors.models import Connector
from bamboo_lib.models import EasyPipeline, PipelineStep, Parameter
from bamboo_lib.steps import DownloadStep, LoadStep

from acs.static import FIPS_CODE, LIST_STATE, DICT_APIS, NULL_LIST
from acs.helper import create_geoid_in_df
from acs.helper_2 import read_by_zone
from static import DICT_RENAME

api_key = os.environ['API_KEY']

class TransformStep(PipelineStep):
    def run_step(self, prev, params):
        year = params.get('year')
        estimate = params.get('estimate')

        list_apis = [
            DICT_APIS['acs_ygi_industry_for_median_earnings_1'], 
            DICT_APIS['acs_ygi_industry_for_median_earnings_2']
        ]

        def transform_by_zone(year, geo, estimate, apis, api_key):
            df = read_by_zone(year, geo, estimate, apis, api_key)
            df = create_geoid_in_df(df, geo)
            df.set_index('geoid', inplace=True)
            df.rename(columns = DICT_RENAME, inplace=True)

            list_all = [
                        [col for col in df.columns if col[0:3] == 'mea'], 
                        [col for col in df.columns if col[0:3] == 'moe']
                        ]

            df_list = []
        
            for i in list_all:
                measure = i[0][0:9]
                df_type = df[i].transpose().reset_index()
            
                df_type[['measure1', 'dim']] = df_type['index'].str.split("-",expand=True)
                df_type[['dim_0', 'dim_1']] = df_type['dim'].str.split("_",expand=True)
               
                df_type.drop(columns = ['index', 'dim'], inplace=True)
                df_type.set_index(['dim_0', 'dim_1'], inplace=True)
                df_type = df_type.transpose().unstack(level=0).reset_index()

                df_type.rename(columns = {0: measure}, inplace=True)
                df_type = df_type[df_type['geoid'] != 'measure1']

                df_list.append(df_type)
                             
            df_all = pd.merge(df_list[0], df_list[1], on=['dim_0', 'dim_1', 'geoid'])
            df_all['year'] = year
            return df_all
        
        df_final = pd.DataFrame()
        list_geo = ['us', 'state', 'county', 'place', 'public use microdata area', 'metropolitan statistical area/micropolitan statistical area', 'congressional district']
      
        for zone in list_geo:
            df_geo = transform_by_zone(year, zone, estimate, list_apis, api_key)
            df_final = df_final.append(df_geo).reset_index(drop=True)
        
        df_final[['dim_0', 'dim_1']] = df_final[['dim_0', 'dim_1']].astype(int)
        list_dim = [2, 3, 9, 10, 13, 14, 16, 17, 18, 20, 21, 23, 24]

        df_final['mea_|v|_0'] = df_final.swifter.apply(lambda x: np.nan if x['dim_1'] in list_dim else x['mea_|v|_1'], axis=1)
        df_final['moe_|v|_0'] = df_final.swifter.apply(lambda x: np.nan if x['dim_1'] in list_dim else x['moe_|v|_1'], axis=1)
        
        df_final[['mea_|v|_0', 'moe_|v|_0', 'mea_|v|_1', 'moe_|v|_1']] = df_final[['mea_|v|_0', 'moe_|v|_0', 'mea_|v|_1', 'moe_|v|_1']].astype(float)
        df_final.replace(NULL_LIST, np.nan, inplace=True)
        
        return df_final

class AcsYgiIndustryForMedianEarningsPipeline(EasyPipeline):
    @staticmethod
    def parameter_list():
        return[
            Parameter(label='year', name='year', dtype=str),
            Parameter(label='estimate', name='estimate', dtype=str),
            Parameter(label='server', name='server', dtype=str)
        ]
    
    @staticmethod
    def steps(params):
        db_connector = Connector.fetch(params.get('server'), open('../../conns.yaml'))
        
        dtype = {
            'year': 'smallint',
            'moe_|v|_0': 'float',
            'mea_|v|_0': 'float',
            'moe_|v|_1': 'float',
            'mea_|v|_1': 'float',
            'dim_0': 'int',
            'dim_1': 'int',
            'geoid': 'text'
        }

        transform_step = TransformStep()

        load_step = LoadStep(
            "acs_ygi_industry_for_median_earnings_{}".format(params.get('estimate')), db_connector, if_exists='append',
            schema='acs', dtype=dtype, pk=['geoid', 'dim_0', 'dim_1'], nullable_list=['mea_|v|_0', 'moe_|v|_0', 'mea_|v|_1', 'moe_|v|_1']
        )

        return [transform_step, load_step]
        
if __name__ == '__main__':
    acs_pipeline = AcsYgiIndustryForMedianEarningsPipeline()
    for estimate in ['1', '5']:
        for year in range(2013, 2019 + 1):
            acs_pipeline.run({
                'year': year,
                'estimate': estimate,
                'server': 'monet-backend'
            })