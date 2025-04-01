#!/bin/bash

table=$1

# Check if a table name is passed as an argument
if [ -z "$table" ]; then
  echo "Error: No table name specified."
  exit 1
fi

# Path to the compressed and uncompressed file
csv_file="/home/deploy/backups/acs/${table}.csv"
csv_gz_file="/home/deploy/backups/acs/${table}.csv.gz"

# Step 1: Unzip the .csv.gz file
echo "Unzipping $csv_gz_file ..."
sudo gzip -d "$csv_gz_file"

# Check if the unzip was successful
if [ $? -ne 0 ]; then
  echo "Error: Failed to unzip the file."
  exit 1
fi

# Step 2: Ingest data into ClickHouse
echo "Ingesting data into table $table ..."
#cat "$csv_file" | clickhouse-client --query="INSERT INTO $table FORMAT CSV NULL=''"
clickhouse-client --database=datausa_db --password=$PWD --query="INSERT INTO $table FORMAT CSV" < "$csv_file"

# Check if the ingestion was successful
if [ $? -ne 0 ]; then
  echo "Error: Failed to ingest data into ClickHouse."
  exit 1
fi

echo "Process completed for table $table."
