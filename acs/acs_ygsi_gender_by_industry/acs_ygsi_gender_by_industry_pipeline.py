import requests
import numpy as np
import pandas as pd
import os

from bamboo_lib.connectors.models import Connector
from bamboo_lib.models import EasyPipeline, PipelineStep, Parameter
from bamboo_lib.steps import DownloadStep, LoadStep

from acs.static import FIPS_CODE, LIST_STATE, DICT_APIS, NULL_LIST
from acs.helper import create_geoid_in_df, read_file
from acs.helper_2 import read_by_zone
from static import DICT_RENAME, DICT_RENAME2023

api_key = os.environ['API_KEY']

class TransformStep(PipelineStep):
    def run_step(self, prev, params):
        year = params.get('year')
        estimate = params.get('estimate')

        list_apis = [
            DICT_APIS['acs_ygsi_gender_by_industry_1'], 
            DICT_APIS['acs_ygsi_gender_by_industry_2'],
            DICT_APIS['acs_ygsi_gender_by_industry_3'], 
            DICT_APIS['acs_ygsi_gender_by_industry_4'],
            DICT_APIS['acs_ygsi_gender_by_industry_5'], 
            DICT_APIS['acs_ygsi_gender_by_industry_6'],
            DICT_APIS['acs_ygsi_gender_by_industry_7'], 
            DICT_APIS['acs_ygsi_gender_by_industry_8'],
            DICT_APIS['acs_ygsi_gender_by_industry_9']
        ]

        if int(year)>=2023: #Modify acs_ygsi_gender_by_industry_5 api
            deleted_columns=['B24030_206E,','B24030_206M,',
                             'B24030_207E,','B24030_207M,',
                             'B24030_208E,','B24030_208M,',
                             'B24030_209E,','B24030_209M,',]
            for col in deleted_columns:
                
                list_apis[4][0]=list_apis[4][0].replace(col,'')
            list_apis[4][1]=list_apis[4][0]+'&in=state:{}'
            
        def transform_by_zone(year, geo, estimate, apis, api_key):
            df = read_file('/home/deploy/datausa-acs-bamboo-etl/acs/data/B24030_2014.csv') if str(year) == '2014' and estimate == '1' and geo == 'us' else read_by_zone(year, geo, estimate, apis, api_key)
            df = create_geoid_in_df(df, geo)
            df.set_index('geoid', inplace=True)

            df.rename(columns = DICT_RENAME, inplace=True) if int(year) < 2023 else df.rename(columns = DICT_RENAME2023, inplace=True)  #I add this :)

            list_all = [
                        [col for col in df.columns if col[0:3] == 'mea'], 
                        [col for col in df.columns if col[0:3] == 'moe']
                        ]

            df_list = []
        
            for i in list_all:
                measure = i[0][0:3]
                df_type = df[i].transpose().reset_index()
            
                df_type[['measure1', 'dim']] = df_type['index'].str.split("-",expand=True)
                df_type[['dim_0', 'dim_1', 'dim_2', 'dim_3']] = df_type['dim'].str.split("_",expand=True)
               
                df_type.drop(columns = ['index', 'dim'], inplace=True)
                df_type.set_index(['dim_0', 'dim_1', 'dim_2', 'dim_3'], inplace=True)
                df_type = df_type.transpose().unstack(level=0).reset_index()

                df_type.rename(columns = {0: measure}, inplace=True)
                df_type = df_type[df_type['geoid'] != 'measure1']

                df_list.append(df_type)
                             
            df_all = pd.merge(df_list[0], df_list[1], on=['dim_0', 'dim_1', 'dim_2', 'dim_3', 'geoid'])
            df_all['year'] = year
            return df_all
        
        df_final = pd.DataFrame()
        list_geo = ['us', 'state', 'county', 'place', 'public use microdata area', 'metropolitan statistical area/micropolitan statistical area', 'congressional district']
      
        for zone in list_geo:
            df_geo = transform_by_zone(year, zone, estimate, list_apis, api_key)
            df_final = df_final.append(df_geo).reset_index(drop=True)
        
        df_final[['dim_0', 'dim_1', 'dim_2', 'dim_3']] = df_final[['dim_0', 'dim_1', 'dim_2', 'dim_3']].astype(int)     
        df_final[['mea', 'moe']] = df_final[['mea', 'moe',]].astype(float)
        df_final.replace(NULL_LIST, np.nan, inplace=True)

        return df_final

class AcsYgsiGenderByIndustryPipeline(EasyPipeline):
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
            'year':     'UInt16',
            'moe':      'UInt32',
            'mea':      'UInt32',
            'dim_0':    'UInt8',
            'dim_1':    'UInt8',
            'dim_2':    'UInt8',
            'dim_3':    'UInt8',
            'geoid':    'String'
        }

        transform_step = TransformStep()

        load_step = LoadStep(
            "acs_ygsi_gender_by_industry_{}".format(params.get('estimate')), db_connector, if_exists='append', dtype=dtype, pk=['geoid', 'year'], nullable_list=['mea', 'moe']
        )

        return [transform_step, load_step]
        
if __name__ == '__main__':
    acs_pipeline = AcsYgsiGenderByIndustryPipeline()
    for estimate in ['1']:
        for year in range(2023, 2023 + 1):
            acs_pipeline.run({
                'year': year,
                'estimate': estimate,
                'server': 'clickhouse-database'
            })
