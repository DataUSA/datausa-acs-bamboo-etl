import requests
import numpy as np
import pandas as pd
import os
import swifter

from bamboo_lib.connectors.models import Connector
from bamboo_lib.models import EasyPipeline, PipelineStep, Parameter
from bamboo_lib.steps import DownloadStep, LoadStep

from acs.static import FIPS_CODE, LIST_STATE, DICT_APIS
from acs.helper import read_by_zone, create_geoid_in_df
from static import DICT_RENAME

api_key = os.environ['API_KEY']

class TransformStep(PipelineStep):
    def run_step(self, prev, params):
        year = params.get('year')
        estimate = params.get('estimate')
        apis = DICT_APIS['acs_yg_household_income']

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
                measure = i[0][0:3]
                df_type = df[i].transpose().reset_index()
             
                df_type[['measure1', 'dim_0']] = df_type['index'].str.split("-",expand=True)
    
                df_type.drop(columns = ['index'], inplace=True)
                df_type.set_index('dim_0', inplace=True)
                df_type = df_type.transpose().unstack(level=0).reset_index()

                df_type.rename(columns = {0: measure}, inplace=True)
                df_type = df_type[df_type['geoid'] != 'measure1']

                df_list.append(df_type)
                             
            df_all = pd.merge(df_list[0], df_list[1], on=['dim_0', 'geoid'])
            df_all['year'] = year
            return df_all
        
        df_final = pd.DataFrame()
        list_geo = ['us', 'state', 'county', 'place', 'public use microdata area', 'metropolitan statistical area/micropolitan statistical area', 'congressional district']

        for zone in list_geo:
            df_geo = transform_by_zone(year, zone, estimate, apis, api_key)
            df_final = df_final.append(df_geo).reset_index(drop=True)
        
        df_final[['mea', 'moe']] = df_final[['mea', 'moe']].astype(float)

        return df_final

class AcsYgHouseholdIncomePipeline(EasyPipeline):
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
            'moe': 'float',
            'mea': 'float',
            'dim_0': 'int',
            'geoid': 'text'
        }

        transform_step = TransformStep()

        load_step = LoadStep(
            "acs_yg_household_income_{}".format(params.get('estimate')), db_connector, if_exists='append',
            schema='acs', dtype=dtype, pk=['geoid', 'dim_0'], nullable_list=['moe', 'mea']
        )

        return [transform_step, load_step]
        
if __name__ == '__main__':
    acs_pipeline = AcsYgHouseholdIncomePipeline()
    for estimate in [1, 5]:
        for year in range(2013, 2019 + 1):
            acs_pipeline.run({
                'year': year,
                'estimate': estimate,
                'server': 'monet-backend'
            })