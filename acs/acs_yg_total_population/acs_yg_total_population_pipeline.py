import requests
import numpy as np
import pandas as pd
import os
 

from bamboo_lib.connectors.models import Connector
from bamboo_lib.models import EasyPipeline, PipelineStep, Parameter
from bamboo_lib.steps import DownloadStep, LoadStep

from acs.static import FIPS_CODE, LIST_STATE, DICT_APIS, NULL_LIST
from acs.helper import read_by_zone, create_geoid_in_df, read_file

api_key = os.environ['API_KEY']

class TransformStep(PipelineStep):
    def run_step(self, prev, params):
        year = params.get('year')
        estimate = params.get('estimate')
        apis = DICT_APIS['acs_yg_total_population']

        def transform_by_zone(year, geo, estimate, apis, api_key):
            df = read_file('/home/deploy/datausa-acs-bamboo-etl/acs/data/B01003_2014.csv') if str(year) == '2014' and estimate == '1' and geo == 'us' else read_by_zone(year, geo, estimate, apis, api_key)
            df = create_geoid_in_df(df, geo)
            df.rename(columns = {'B01003_001E': 'mea', 'B01003_001M': 'moe'}, inplace=True)
            df['year'] = year
            df = df[['moe', 'mea', 'year', 'geoid']]
            return df

        df_final = pd.DataFrame()

        list_geo = ['us', 'state', 'county', 'place', 'public use microdata area', 'metropolitan statistical area/micropolitan statistical area', 'congressional district'] if estimate == '1' else ['us', 'state', 'county', 'place', 'public use microdata area', 'metropolitan statistical area/micropolitan statistical area', 'tract', 'congressional district']

        for zone in list_geo:
            df_geo = transform_by_zone(year, zone, estimate, apis, api_key)
            df_final = df_final.append(df_geo).reset_index(drop=True)

        df_final.replace('*****', np.nan, inplace=True)
        df_final[['mea', 'moe']] = df_final[['mea', 'moe']].astype(float)
        df_final.replace(NULL_LIST, np.nan, inplace=True)

        return df_final

class AcsYgTotalPopulationPipeline(EasyPipeline):
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
            'moe': 'UInt16',
            'mea': 'UInt32',
            'geoid': 'String'
        }

        transform_step = TransformStep()

        load_step = LoadStep(
            "acs_yg_total_population_{}".format(params.get('estimate')), db_connector, if_exists = 'append',
            dtype = dtype, pk = ['geoid', 'year'], nullable_list=['moe', 'mea']
        )

        return [transform_step, load_step]

if __name__ == '__main__':
    acs_pipeline = AcsYgTotalPopulationPipeline()
    for estimate in ['1', '5']:
        for year in range(2013, 2020 + 1):      
            if year == 2020 and estimate == "1":
                continue
            else:
                acs_pipeline.run({
                    'year': year,
                    'estimate': estimate,
                    'server': 'clickhouse-database'
                })