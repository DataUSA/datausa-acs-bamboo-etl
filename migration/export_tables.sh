#!/bin/bash


query_read="SELECT name
FROM sys.tables
WHERE schema_id = (SELECT id FROM sys.schemas WHERE name = 'acs');"

mclient -d datausa -s "$query_read" > temp_file.txt
grep "|" temp_file.txt | awk -F '|' '{print $2}' > clean_tables.txt

DEST_DIR=$0
TABLES_FILE="temp_file.txt"

# Create destination directory if it doesn't exist
mkdir -p "$DEST_DIR"

# Check if the tables file exists
if [ ! -f "$TABLES_FILE" ]; then
    echo "Error: The file $TABLES_FILE does not exist"
    exit 1
fi

# Create temporary directory for CSV files
TEMP_DIR="$DEST_DIR/temp_csv"
mkdir -p "$TEMP_DIR"

# Export each table to CSV
while IFS= read -r table; do
    echo "Exporting table: $table"
    
    # Export table to CSV using monetdb
    mclient -u monetdb -d datausa  -p $DATAUSA_DB_PW -s "COPY SELECT * FROM acs.$table INTO '$TEMP_DIR/${table}.csv' USING DELIMITERS ',' '\n' '\"' NULL AS '\N';"
    
    # Compress the CSV file
    gzip "$TEMP_DIR/${table}.csv"
done < "$TABLES_FILE"

# Compress the entire temporary directory
tar -czf "$DEST_DIR/tables_acs_backup.tar.gz" -C "$TEMP_DIR" .

# Clean up temporary files
rm -rf "$TEMP_DIR"

echo "Process completed. Compressed files are located at: $DEST_DIR/tables_acs_backup.tar.gz" 