#!/bin/bash

# Parse arguments (2)
if [ $# -ne 2 ]; then
  echo "Usage: $0 <YEAR> <SERVER>"
  exit 1
fi

YEAR=$1
SERVER=$2

# Assign arguments to variable
export YEAR="$1" # ex. 2023
export SERVER="$2" # ex. default


export REPOSITORY_PATH="/datausa-acs-bamboo-etl"
export ESTIMATES=("1" "5")
export PP_YEAR=$YEAR;
export PYTHON_FILES=$(find "/datausa-acs-bamboo-etl/acs" -type f -name "acs_*_pipeline.py")

mkdir -p $REPOSITORY_PATH/updates/logs;
mkdir -p $REPOSITORY_PATH/updates/logs/$PP_YEAR/$SERVER/1;
mkdir -p $REPOSITORY_PATH/updates/logs/$PP_YEAR/$SERVER/5;


for ESTIMATE in "${ESTIMATES[@]}"; do
    for PIPELINE_REPOSITORY_PATH in $PYTHON_FILES; do
        export PIPELINE_DIR=$(dirname $PIPELINE_REPOSITORY_PATH)
        export FILE_NAME=$(basename $PIPELINE_REPOSITORY_PATH .py)
        export PIPELINE_NAME=${FILE_NAME%%_pipeline}
        echo ;
        echo Running: $PIPELINE_NAME-$ESTIMATE-$SERVER;

        bash -c "export PIPELINE_NAME=$PIPELINE_NAME;export ESTIMATE=$ESTIMATE;export PP_YEAR=$PP_YEAR;export FILE_NAME=$FILE_NAME;export SERVER=$SERVER;cd $PIPELINE_DIR;bamboo-cli --folder . --entry $FILE_NAME --year=$PP_YEAR --estimate=$ESTIMATE --server=$SERVER;" >> "$REPOSITORY_PATH/updates/logs/$PP_YEAR/$SERVER/$ESTIMATE/$PIPELINE_NAME-$ESTIMATE.log" 2>&1
        
        sleep 5

        echo Done: $PIPELINE_NAME-$ESTIMATE-$SERVER;
        echo ;
    done
done
