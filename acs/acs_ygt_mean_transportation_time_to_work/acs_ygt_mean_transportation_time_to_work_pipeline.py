import requests
import numpy as np
import pandas as pd
import os

from bamboo_lib.connectors.models import Connector
from bamboo_lib.models import EasyPipeline, PipelineStep, Parameter
from bamboo_lib.steps import DownloadStep, LoadStep

from acs.static import FIPS_CODE, LIST_STATE, DICT_APIS, NULL_LIST
from acs.helper import read_by_zone, create_geoid_in_df, empty_str_replace

api_key = os.environ['API_KEY']

class TransformStep(PipelineStep):
    def run_step(self, prev, params):
        year = params.get('year')
        estimate = params.get('estimate')
        apis = DICT_APIS['acs_ygt_mean_transportation_time_to_work']

        def transform_by_zone(year, geo, estimate, apis, api_key):
            if str(year) == '2014' and estimate == '1' and geo == 'us': 
                df_B08013 = pd.read_csv('/home/deploy/datausa-acs-bamboo-etl/acs/data/B08013_2014.csv')[1::]
                df_B08006 = pd.read_csv('/home/deploy/datausa-acs-bamboo-etl/acs/data/B08006_2014.csv')[1::]

                df_B08013 = df_B08013[['GEO_ID', 'B08013_001E']]
                df_B08006 = df_B08006[['GEO_ID', 'B08006_001E', 'B08006_017E']]
            
                df = pd.merge(df_B08013, df_B08006, on=['GEO_ID'])

            else:
                df = read_by_zone(year, geo, estimate, apis, api_key)

            df = create_geoid_in_df(df, geo)
    
            df[['B08013_001E', 'B08006_001E','B08006_017E']] = df[['B08013_001E', 'B08006_001E','B08006_017E']].astype(float)
            df.replace(NULL_LIST, np.nan, inplace=True)

            df['mea'] = df.apply(lambda x: x['B08013_001E'] / (x['B08006_001E'] - x['B08006_017E']) if x['B08013_001E'] != np.nan and x['B08006_001E'] != np.nan and x['B08006_017E']!= np.nan and (x['B08006_001E'] - x['B08006_017E']) != 0 else np.nan, axis=1)
            df['moe'] = np.nan

            df['mea'] = df['mea'].apply(lambda x: empty_str_replace(x))

            df['year'] = year
            df = df[['moe', 'mea', 'year', 'geoid']]
            return df

        df_final = pd.DataFrame()

        list_geo = ['us', 'state', 'county', 'place', 'public use microdata area', 'metropolitan statistical area/micropolitan statistical area', 'congressional district'] if estimate == '1' else ['us', 'state', 'county', 'place', 'public use microdata area', 'metropolitan statistical area/micropolitan statistical area', 'tract', 'congressional district']

        for zone in list_geo:
            df_geo = transform_by_zone(year, zone, estimate, apis, api_key)
            df_final = df_final.append(df_geo).reset_index(drop=True)
        
        df_final[['mea', 'moe']] = df_final[['mea', 'moe']].astype(float)
        df_final.replace(NULL_LIST, np.nan, inplace=True)

        return df_final

class AcsYgtMeanTransportationTimeToWorkPipeline(EasyPipeline):
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
            'geoid': 'text'
        }
        

        transform_step = TransformStep()

        load_step = LoadStep(
            "acs_ygt_mean_transportation_time_to_work_{}".format(params.get('estimate')), db_connector, if_exists = 'append',schema= 'acs', dtype = dtype, pk = ['geoid'], nullable_list=['moe', 'mea']
        )

        return [transform_step, load_step]

if __name__ == '__main__':
    acs_pipeline = AcsYgtMeanTransportationTimeToWorkPipeline()
    for estimate in ['1', '5']:
        for year in range(2013, 2020 + 1):
            if estimate == '1' and year ==2020:
                continue
            else:
                acs_pipeline.run({
                    'year': year,
                    'estimate': estimate,
                    'server': 'monet-backend'
                })
