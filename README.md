# Data USA ACS Bamboo ETL

This repository will have a series of Bamboo pipelines to process and ingest the data from the American Community Survey used in Data USA.

## Local Setup

1. Create a new virtual environment and activate it:
```
python -m venv venv
source venv/bin/activate
```

2. Install requirements
```
pip install -r requirements.txt
```

3. Create an environment variables file following this structure:
```
export API_KEY='<Your API KEY goes here>';
export DATAUSA_DB_PW='monetdb'; # The default password for MonetDB is monetdb.
export DATAUSA_DB_HOST='localhost'; # Assuming you're ingesting inside a local MonetDB container.
export PYTHONPATH=$PYTHONPATH:<path to repository>/datausa-acs-bamboo-etl;
```

4. Run a pipeline, for example, the Gini pipeline:
```
source .env
cd acs/acs_yg_gini
python acs_yg_gini_pipeline.py
```

## Dockerized Setup

1. Create Python 3.7.9 container:
```
docker run -it -v <path to repository>/datausa-acs-bamboo-etl:/datausa-acs-bamboo-etl --name=python3-local python:3.7.9 bash
```

2. Use previously created `.env` file and run a pipeline, say the Gini pipeline:
```
cd datausa-acs-bamboo-etl
pip install -r requirements.txt
source .env
cd acs/acs_yg_gini
python acs/acs_yg_gini_pipeline.py
```
