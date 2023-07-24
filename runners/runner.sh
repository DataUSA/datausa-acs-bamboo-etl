#!/bin/bash
export DATAUSA_PATH="/code/datausa/datausa-acs-bamboo-etl";
mkdir -p $DATAUSA_PATH/runners/logs;
export SERVERS=("monet-backend" "postgres-zcube")
export ESTIMATES=("1" "5")
export PP_YEAR="2021";
export PYTHON_FILES=$(find "$DATAUSA_PATH/acs" -type f -name "*_pipeline.py")

for SERVER in "${SERVERS[@]}"; do
    for ESTIMATE in "${ESTIMATES[@]}"; do
        for PIPELINE_PATH in $PYTHON_FILES; do
            export PIPELINE_DIR=$(dirname $PIPELINE_PATH)
            export FILE_NAME=$(basename $PIPELINE_PATH .py)
            export PIPELINE_NAME=${FILE_NAME%%_pipeline}
            echo Running-$PIPELINE_NAME;
            echo ;
            screen -S "$PIPELINE_NAME-$SERVER-$ESTIMATE" -dm -L -Logfile "$DATAUSA_PATH/runners/logs/$PIPELINE_NAME-$SERVER-$ESTIMATE.log" bash -c "export PIPELINE_NAME=$PIPELINE_NAME;export SERVER=$SERVER;export ESTIMATE=$ESTIMATE;export PP_YEAR=$PP_YEAR;export FILE_NAME=$FILE_NAME;source $DATAUSA_PATH/venv/bin/activate;source $DATAUSA_PATH/.env;cd $PIPELINE_DIR;bamboo-cli --folder . --entry $FILE_NAME --year=$PP_YEAR --estimate=$ESTIMATE --server=$SERVER;";
            echo Done Running-$PIPELINE_NAME;
        done
    done
done


