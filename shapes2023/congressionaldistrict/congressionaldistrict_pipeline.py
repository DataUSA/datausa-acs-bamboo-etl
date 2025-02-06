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
        
        
        
        ##COMPLEMENT WITH STATE SHAPE: (adding 'state_name', 'state_id', 'stusps' and 'statefp')
        df_state=query_to_df(self.connector,'SELECT statefp,name as state_name, geoid as state_id, stusps FROM shapes2018.states')  #States shapes from Postgres
        df_state['statefp']=df_state['statefp'].astype(int) #Number of state as a integer number
        df=pd.merge(df,df_state,on='statefp',how='left')


        #CREATE NAME AND SLUG (Columns from previus format)
        df['name']= df['namelsad']+', '+df['stusps']  #Ex. Congressional District 1, AL
        df['slug']= df['name'].str.replace(' ','-',regex=False).str.replace(',','',regex=False).str.lower() #Ex. congressional-district-1-al
        

        #CREATE GEOID (Using the structure '50000US'+STATE NUMBER + DISTRICT NUMBER)
        df['geoidfq']='50000US' + df['geoid']
        df['geoidfq']=df['geoidfq'].str.replace('Z','0',regex=False) #In case of congressional districts not defined, the geoid is ZZ at the end, so i replace it by 00 
        df=df.drop(columns=['stusps','geoid','unnamed: 0'])
        df=df.rename(columns={'geoidfq':'geoid','geometry':'geom','cd119fp':'cdfp'}) #Rename columns to match with db  
        

        #Congressional districts merge with old table:
        df_districts=query_to_df(self.connector,'SELECT geoid, cdsessn as first_cdsessn FROM shapes2018.congressionaldistrict')

        df=pd.merge(df,df_districts,on='geoid',how='outer') #I keep the news values in df
        df=df.drop(columns='first_cdsessn') #Necessary only for a moment in this case

        
        #second merge:
        df_districts_old=df.query('cdsessn!=119')['geoid']  #I keep only the values that df doesnt have. So thats are the old districts (cdsessn 116)
        
        df_districts=query_to_df(self.connector,'SELECT * FROM shapes2018.congressionaldistrict')  #Bring the 2018 congress data (cdsessn 116)
        
        df_districts=pd.merge(df_districts_old,df_districts,on='geoid',how='left') #I keel only the values that df doesn't have (In simple words are the districts that are not in df because thet were deleted)
        df_districts=df_districts.drop(columns='gid') #I'll create new gid value at the end
        df_districts=df_districts.rename(columns={'cd116fp':'cdfp'})
        
        
        #I need reorder de columns because pandas 0.24.2 doesn't order the columns to concatenate
        df.columns = df.columns.str.strip().str.lower()
        df_districts.columns = df_districts.columns.str.strip().str.lower()
        df_districts = df_districts[df.columns]

        #Concatenate the new data with the deleted districts in cdssesn 119
        df = pd.concat([df.query('cdsessn==119'), df_districts], ignore_index=True)
        df=df.reset_index(drop=True)
        df=df.drop(columns='geom')  #I don't need geometry (for now at least)
        df['gid']=range(1, len(df) + 1) #I create a new gid
        df['gid']=df['gid'].astype(int)
        #print('shape final df:',df.shape[0])
        #print(df.head())
 
        return df

class CongressionalDistrict2023Pipeline(EasyPipeline):
    @staticmethod
    def parameter_list():
        return[
            Parameter(label='server', name='server', dtype=str)
        ]
    
    @staticmethod
    def steps(params):
        db_connector = Connector.fetch(params.get('server'), open('../../conns.yaml'))
        
        dtype = {
            'gid': 'serial',   #It's the PK and can't be null
            'statefp':'text',
            'cdfp':'text',
            'geoid':'text',
            'namelsad':'text',
            'lsad':'text',
            'cdsessn':'text',
            'mtfcc':'text',
            'funcstat':'text',
            'aland':'float',
            'awater':'float',
            'intptlat':'text',
            'intptlon':'text',
            'state_name':'text',
            'state_id':'text',
            'name':'text',
            'slug':'text'
        }
        

        transform_step = TransformStep(connector=db_connector)

        load_step = LoadStep(
            'congressionaldistrict', db_connector, if_exists='append',
            schema='shapes2023', dtype=dtype, pk=['gid'], nullable_list=['statefp','cdfp','geoid','namelsad','lsad','cdsessn','mtfcc','funcstat','aland','awater','intptlat','intptlon','state_name','state_id','name','slug']
        ) #All can be null except gid

        return [transform_step,load_step]
        
if __name__ == '__main__':
    shape_pipeline = CongressionalDistrict2023Pipeline()
    shape_pipeline.run({'server': 'postgres-zcube'})