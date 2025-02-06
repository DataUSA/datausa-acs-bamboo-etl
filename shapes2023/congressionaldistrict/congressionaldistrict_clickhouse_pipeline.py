import requests
import numpy as np
import pandas as pd
import os
 
from bamboo_lib.connectors.models import Connector
from bamboo_lib.helpers import query_to_df
from bamboo_lib.models import EasyPipeline, PipelineStep, Parameter
from bamboo_lib.steps import DownloadStep, LoadStep

class TransformStep(PipelineStep):
    def run_step(self, prev, params):
        #All congressional state districts data from 2024
        df=pd.read_csv('../complementary-files/congressional_state_data_2024.csv')
        
        column_names=list(df.columns)
        new_column_names= [i.lower() for i in column_names]  #Columns in db were in lower font, so i need use the same format
        df.columns = new_column_names  #I replace columns name by the same but in lower font
        print('shape df before merge state:',df.shape[0],'Linea 19')
        
        
        ##COMPLEMENT WITH STATE SHAPE: (adding 'state_name', 'state_id', 'stusps' and 'statefp')
        df_state=query_to_df(self.connector,'SELECT statefp,name as state_name, geoid as state_id, stusps FROM states_shapes2017')  #States shapes from Postgres
        df_state['statefp']=df_state['statefp'].astype(int) #Number of state as a integer number
        df=pd.merge(df,df_state,on='statefp',how='left')
        print('shape df after merge state:',df.shape[0],'linea 26')

        #CREATE NAME AND SLUG (Columns from previus format)
        df['name']= df['namelsad']+', '+df['stusps']  #Ex. Congressional District 1, AL
        df['slug']= df['name'].str.replace(' ','-',regex=False).str.replace(',','',regex=False).str.lower() #Ex. congressional-district-1-al
        

        #CREATE GEOID (Using the structure '50000US'+STATE NUMBER + DISTRICT NUMBER)
        df['geoidfq']='50000US' + df['geoid']
        df['geoidfq']=df['geoidfq'].str.replace('Z','0',regex=False) #In case of congressional districts not defined, the geoid is ZZ at the end, so i replace it by 00 
        df=df.drop(columns=['stusps','geoid','unnamed: 0','geometry']) #Clickhouse table doesn't have geometry column
        df=df.rename(columns={'geoidfq':'geoid','cd119fp':'cdfp'}) #Rename columns to match with db  
        



        #Congressional districts merge with old table:
        df_districts=query_to_df(self.connector,'SELECT geoid, cdsessn as first_cdsessn FROM congressional_district_backup')

        df=pd.merge(df,df_districts,on='geoid',how='outer') #I keep the news values in df
        print(df.shape[0],'linea 47') #514 


        #second merge:
        df_districts_old=df.query('cdsessn!=119')[['geoid','first_cdsessn']]  #I keep only the values that df doesnt have. So thats are the old districts (cdsessn 116)
        df_districts=query_to_df(self.connector,'SELECT * FROM congressional_district_backup')  #Bring the 2018 congress data (cdsessn 116)
        df_districts=pd.merge(df_districts_old,df_districts,on='geoid',how='left') #I keel only the values that df doesn't have (In simple words are the districts that are not in df because thet were deleted)
        df_districts=df_districts.rename(columns={'cd116fp':'cdfp'})


        #I need reorder de columns because pandas 0.24.2 doesn't order the columns to concatenate
        df.columns = df.columns.str.strip().str.lower()
        df_districts.columns = df_districts.columns.str.strip().str.lower()
        df_districts = df_districts[df.columns]

        #Concatenate the new data with the deleted districts in cdssesn 119
        df = pd.concat([df.query('cdsessn==119'), df_districts], ignore_index=True)
        print(df.shape[0],'linea 66') #538

        #To upload into clickhouse, i need to convert the columns to the correct format
        df['statefp']=df['statefp'].astype(str)
        df['intptlat']=df['intptlat'].astype(str)
        df['intptlon']=df['intptlon'].astype(str)
        df=df.reset_index(drop=True)

        return df

class CongressionalDistrict2023ClickhousePipeline(EasyPipeline):
    @staticmethod
    def parameter_list():
        return[]
    
    @staticmethod
    def steps(params):
        db_connector = Connector.fetch('clickhouse-database', open('../../conns.yaml'))
        
        dtype={'statefp':'String',
               'cdfp':'String',
               'namelsad':'String',
               'lsad':'String',
               'cdsessn':'UInt8',
               'first_cdsessn':'UInt8',
               'mtfcc':'String',
               'funcstat' :'String',
               'aland':'Float32',
               'awater':'Float32',
               'intptlat' :'String',
               'intptlon' :'String',
               'name' :'String',
               'geoid': 'String',
               'slug':'String',
               'state_id': 'String',
               'state_name': 'String'
               }    
        

        transform_step = TransformStep(connector=db_connector)

        load_step = LoadStep('congressional_district',db_connector, if_exists='append',dtype=dtype, pk=['geoid'], nullable_list=['lsad','first_cdsessn','cdsessn','mtfcc','funcstat','aland','awater','intptlat','intptlon'])

        return [transform_step,load_step]
        
if __name__ == '__main__':
    shape_pipeline = CongressionalDistrict2023ClickhousePipeline()
    shape_pipeline.run({})