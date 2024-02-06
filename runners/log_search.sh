#!/bin/bash

# Define the search string
search_string="Traceback (most recent call last):"

# Create or overwrite the result.txt file
> result.txt

# Iterate through log files and search for the error
find ./logs -type f -name "*.log" -exec grep -l "$search_string" {} + >> result.txt

echo "Files containing the error have been listed in result.txt"