#!/bin/bash

# Parse arguments (5)
if [ $# -ne 5 ]; then
  echo "Usage: $0 <DATAUSA_PATH> <VENV_PATH> <SERVER> <YEAR> <ESTIMATE>"
  exit 1
fi

# Assign arguments to variables
export DATAUSA_PATH="$1" # ex. /code/datausa/datausa-acs-bamboo-etl
export VENV_PATH="$2" # ex. ~/venv
export SERVERS="$3" # ex. postgres-zcube or monet-backend
export YEAR="$4" # ex. 2021
export ESTIMATES="$5"


export SERVERS=("$3")
export ESTIMATES=("$5")
export PP_YEAR=$YEAR;
export PYTHON_FILES=$(find "$DATAUSA_PATH/acs" -type f -name "*_pipeline.py")

mkdir -p $DATAUSA_PATH/runners/logs;
for SERVER in "${SERVERS[@]}"; do
    mkdir -p $DATAUSA_PATH/runners/logs/$SERVER/1/$PP_YEAR;
    mkdir -p $DATAUSA_PATH/runners/logs/$SERVER/5/$PP_YEAR;
done

for SERVER in "${SERVERS[@]}"; do
    for ESTIMATE in "${ESTIMATES[@]}"; do
        for PIPELINE_PATH in $PYTHON_FILES; do
            export PIPELINE_DIR=$(dirname $PIPELINE_PATH)
            export FILE_NAME=$(basename $PIPELINE_PATH .py)
            export PIPELINE_NAME=${FILE_NAME%%_pipeline}
            echo Running-$PIPELINE_NAME;
            echo ;
            screen -S "$PIPELINE_NAME-$SERVER-$ESTIMATE" -L -Logfile "$DATAUSA_PATH/runners/logs/$SERVER/$ESTIMATE/$PP_YEAR/$PIPELINE_NAME-$SERVER-$ESTIMATE.log" bash -c "export PIPELINE_NAME=$PIPELINE_NAME;export SERVER=$SERVER;export ESTIMATE=$ESTIMATE;export PP_YEAR=$PP_YEAR;export FILE_NAME=$FILE_NAME;source $VENV_PATH/bin/activate;source $DATAUSA_PATH/.env;cd $PIPELINE_DIR;bamboo-cli --folder . --entry $FILE_NAME --year=$PP_YEAR --estimate=$ESTIMATE --server=$SERVER;";
            echo Done Running-$PIPELINE_NAME;
        done
    done
done


