import requests
import numpy as np
import pandas as pd
import os
 
from bamboo_lib.connectors.models import Connector
from bamboo_lib.models import EasyPipeline, PipelineStep, Parameter
from bamboo_lib.steps import DownloadStep, LoadStep

from acs.static import FIPS_CODE, LIST_STATE, DICT_APIS, NULL_LIST
from acs.helper import read_by_zone, create_geoid_in_df
from static import DICT_RENAME

api_key = os.environ['API_KEY']

class TransformStep(PipelineStep):
    def run_step(self, prev, params):
        year = params.get('year')
        estimate = params.get('estimate')
        apis = DICT_APIS['acs_health_coverage_s']

        def transform_by_zone(year, geo, estimate, apis, api_key):
            df = read_by_zone(year, geo, estimate, apis, api_key)
            df = create_geoid_in_df(df, geo)
            df.set_index('geoid', inplace=True)
            df.rename(columns = DICT_RENAME, inplace=True)

            list_all = [
                        [col for col in df.columns if col[0:5] == 'mea_0'], 
                        [col for col in df.columns if col[0:5] == 'moe_0']
                        ]

            df_list = []
    
            for i in list_all:
                measure = i[0][0:5]
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
            df = df[['mea_1', 'mea_2', 'mea_3', 'mea_4', 'moe_1', 'moe_2', 'moe_3', 'moe_4']].reset_index()
            
            df_all = df_all.merge(df, on='geoid', how='left')
            df_all['year'] = year
            return df_all
        
        df_final = pd.DataFrame()
        list_geo = ['us', 'state', 'county', 'place', 'public use microdata area', 'metropolitan statistical area/micropolitan statistical area', 'congressional district'] if estimate == '1' else ['us', 'state', 'county', 'place', 'public use microdata area', 'metropolitan statistical area/micropolitan statistical area', 'tract', 'congressional district']

        for zone in list_geo:
            df_geo = transform_by_zone(year, zone, estimate, apis, api_key)
            df_final = df_final.append(df_geo).reset_index(drop=True)
        
        df_final[['dim_0', 'dim_1']] = df_final[['dim_0', 'dim_1']].astype(int)
        df_final[['mea_0', 'moe_0', 'mea_1', 'mea_2', 'mea_3', 'mea_4', 'moe_1', 'moe_2', 'moe_3', 'moe_4']] = df_final[['mea_0', 'moe_0', 'mea_1', 'mea_2', 'mea_3', 'mea_4', 'moe_1', 'moe_2', 'moe_3', 'moe_4']].astype(float)
        df_final.replace(NULL_LIST, np.nan, inplace=True)

        return df_final

class AcsHealthCoverageSPipeline(EasyPipeline):
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
            'year': 'UInt16',
            'moe_0': 'UInt32',
            'moe_1': 'UInt16',
            'moe_2': 'UInt16',
            'moe_3': 'UInt16',
            'moe_4': 'UInt16',
            'mea_0': 'UInt32',
            'mea_1': 'UInt32',
            'mea_2': 'UInt32',
            'mea_3': 'UInt32',
            'mea_4': 'UInt32',
            'dim_0': 'UInt8',
            'dim_1': 'UInt8',
            'geoid': 'String'
        }

        transform_step = TransformStep()

        load_step = LoadStep(
            "acs_health_coverage_s_{}".format(params.get('estimate')), db_connector, if_exists='append',
            schema='acs', dtype=dtype, pk=['geoid', 'year'], nullable_list=['mea_0', 'mea_1', 'mea_2', 'mea_3', 'mea_4', 'moe_0', 'moe_1', 'moe_2', 'moe_3', 'moe_4']
        )

        return [transform_step, load_step]
        
if __name__ == '__main__':
    acs_pipeline = AcsHealthCoverageSPipeline()
    for estimate in ['1', '5']:
        for year in range(2015, 2020 + 1):
            if year == 2020 and estimate == "1":
                continue
            else:
                acs_pipeline.run({
                    'year': year,
                    'estimate': estimate,
                    'server': 'clickhouse-database'
                })