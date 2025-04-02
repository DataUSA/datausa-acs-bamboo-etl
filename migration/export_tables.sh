#!/bin/bash


query_read="SELECT name
FROM sys.tables
WHERE schema_id = (SELECT id FROM sys.schemas WHERE name = 'acs');"

mclient -d datausa -u monetdb -s "$query_read" > temp_file.txt
grep "|" temp_file.txt | awk -F '|' '{gsub(/^[ \t]+|[ \t]+$/, "", $2); print $2}' > clean_tables.txt

export MONETDB_PASSWD="monetdb"

DEST_DIR="/home/deploy/backup"
TABLES_FILE="clean_tables.txt"

# Create destination directory if it doesn't exist
mkdir -p "$DEST_DIR"

# Check if the tables file exists
if [ ! -f "$TABLES_FILE" ]; then
    echo "Error: The file $TABLES_FILE does not exist"
    exit 1
fi

# Create temporary directory for CSV files
TEMP_DIR="$DEST_DIR/temp_csv"

# Export each table to CSV
while IFS= read -r table; do
    echo "Exporting table: $table .."
    
    # Export table to CSV using monetdb
    mclient -u monetdb -d datausa -s "COPY SELECT * FROM acs.$table INTO '$TEMP_DIR/${table}.csv' USING DELIMITERS ',', '\n', '\"';"
    # Compress the CSV file
    sudo gzip "$TEMP_DIR/${table}.csv"
done < "$TABLES_FILE"

# Compress the entire temporary directory
sudo tar -czf "$DEST_DIR/tables_acs_backup.tar.gz" -C "$TEMP_DIR" .

# Clean up temporary files
#rm -rf "$TEMP_DIR"

echo "Process completed. Compressed files are located at: $DEST_DIR/tables_acs_backup.tar.gz" 