import pandas as pd
import csv
import pymonetdb
import os

from bamboo_lib.connectors.models import Connector
from bamboo_lib.models import EasyPipeline, PipelineStep, Parameter
from bamboo_lib.steps import DownloadStep, LoadStep
from bamboo_lib.logger import logger
from bamboo_lib.helpers import query_to_df

from tables_helper import TABLE_NAMES


class ReadStep(PipelineStep):
    def run_step(self, prev, params):
        logger.info("Reading Database...")

        connection = pymonetdb.connect(
            username = os.environ['DB_USER'], 
            password = os.environ['DB_PW'], 
            hostname = os.environ['DB_HOST'], 
            database = os.environ['DB_NAME']
        )
        cursor = connection.cursor()
        cursor.arraysize = 100

        tables_data = {}

        for table in TABLE_NAMES[0:2:11]:
            tables_data[table] = {}

            # Check Total Rows
            cursor.execute('SELECT COUNT(*) FROM acs.{};'.format(table))
            total_rows = cursor.fetchall()[0][0]
            tables_data[table]["total_rows"] = "{:,}".format(int(total_rows))

            # Check Total Rows by Year
            cursor.execute('SELECT "year", COUNT(*) FROM acs.{} GROUP BY "year" ORDER BY "year";'.format(table))
            year_counts = cursor.fetchall()
            for (y, c) in year_counts:
                tables_data[table][str(y)] = "{:,}".format(int(c))

            # Check Geo Levels by Year
            geo_levels = [
                ('nation', '01000US'), ('state', '04000US__'), ('county','05000US_____'), ('place','16000US______'), 
                ('puma','79500US%'), ('msa','31000US%'), ('tract','14000US%'), ('cd','50000US%'), ('zip','86000US%')
            ]
            for (geo, code) in geo_levels:
                cursor.execute('''SELECT "year", COUNT(*) FROM acs.{} WHERE "geoid" LIKE '{}' GROUP BY "year" ORDER BY "year";'''.format(table, code))
                response = cursor.fetchall()
                print('''SELECT "year", COUNT(*) FROM acs.{} WHERE "geoid" LIKE '{}' GROUP BY "year" ORDER BY "year";'''.format(table, code))
                # If no geo levels are returned
                if len(response) == 0:
                    continue
                elif len(response) > 0:
                    level_counts = [c for (y, c) in response]
                    # If all elements in the list are the same, put the number
                    if level_counts.count(level_counts[0]) == len(level_counts):
                        tables_data[table][geo] = "{:,}".format(int(level_counts[0]))
                    # If not, put the LAST YEAR's value
                    else:
                        tables_data[table][geo] = "{}: {:,}".format(response[-1][0], response[-1][1])
                else:
                    print("FAIL.")

        df = pd.DataFrame.from_dict(tables_data, orient='index')
        print(df)

        df = df[[
            "2013", "2014", "2015", "2016", "2017", "2018", "2019", "total_rows", 
            "nation", "state", "county", "PUMA", "MSA", "CD", "tract", "zip"
        ]]
        
        df.to_csv(params.get("output"), quoting=csv.QUOTE_ALL, sep=";")

        return tables_data

class ACSAnalysisPipeline(EasyPipeline):
    @staticmethod
    def parameter_list():
        return[
            Parameter(label='server', name='server', dtype=str),
            Parameter(label='output', name='output', dtype=str)
        ]

    @staticmethod
    def steps(params):
        db_connector = Connector.fetch(params.get('server'), open('../conns.yaml'))

        read_step = ReadStep()

        return [read_step]


if __name__ == '__main__':
    acs_analysis = ACSAnalysisPipeline()
    acs_analysis.run({
        'server': 'monet-backend',
        'output': 'backend.csv'
    })