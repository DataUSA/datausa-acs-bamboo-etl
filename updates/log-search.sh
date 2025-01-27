#!/bin/bash

# Define the search string
search_string="Traceback (most recent call last):"
other_search_str="WARNING:clickhouse_driver.connection:Error"

# Create or overwrite the result.txt file
> updates/result.txt

# Iterate through log files and search for the error
find ./updates/logs -type f -name "*.log" -exec grep -l -e "$search_string" -e "$other_search_str" {} + >> updates/result.txt

echo "Files containing the error have been listed in updates/result.txt"