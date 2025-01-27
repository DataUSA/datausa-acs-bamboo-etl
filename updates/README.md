# Data updates

## ACS Bash Runner: update-acs.sh
To avoid running every pipeline by itself and taking advantage from the standarization of the codebase, the file `/updates/update-acs.sh` allows to run all ACS pipelines in one command, and create log files for each pipeline execution, so that the success of a pipeline run can be asserted.

## How to use the runner scripts?
### Some things to consider
* It's required to have a *python virtual enviroment* with all the required libraries already created (OR a Docker Container).
* It's required to have a *.env* file such that it includes:

```bash
PYTHONPATH=<PYTHONPATH>
API_KEY=<API_KEY>
DATAUSA_DB_PW=<DATAUSA_DB_PW>
DATAUSA_DB_HOST=<DATAUSA_DB_HOST>
BAMBOO_DB_PW=<BAMBOO_DB_PW>
BAMBOO_DB_HOST=<BAMBOO_DB_HOST>
BAMBOO_DOWNLOAD_FOLDER=/app/tmp/bamboo_downloads
```

### Usage
The script takes a parameter:
1. YEAR: Year to be ingested. ex. 2023.

```bash
$ cd datausa-acs-bamboo-etl
$ screen -S datausa-acs-bamboo
$ docker build . -t datausa-acs-bamboo-etl
$ YEAR=2023
$ SERVER=monet-backend
$ docker run --rm -it -v $(pwd):/datausa-acs-bamboo-etl -v /srv/storage/code_niconetz/tmp:/app/tmp/bamboo_downloads --network="host" --workdir /datausa-acs-bamboo-etl --env-file $(pwd)/.env.local datausa-acs-bamboo-etl:latest bash updates/update-acs.sh $YEAR $SERVER
# The script should start. You should see some terminal output as:

INFO:bamboo_lib.logger:Received parameter with key=year and value=2023
INFO:bamboo_lib.logger:Downloading 2023: us from API...
INFO:bamboo_lib.logger:Downloading 2023: us from API...
# You can detach the screen session by using: Ctrl + a + d
# You can quit the terminal and log back using:
$ screen -ls
There is a screen on:
        2010743.datausa-acs-bamboo (07/24/2024 08:18:56 PM)        (Detached)
1 Socket in /run/screen/S-datausa-acs-bamboo.
$ screen -r datausa-acs-bamboo
# Now you should be back
```

## Data checks
To confirm that the ingestion process was succesful, you need to check all logs located on `/runners/logs/*`. Those are separated in folders, by server, acs estimate and year:

```bash
updates/logs
└── 2023
    ├── county
    │   ├── acs_...-5.log
    │   ├── ...
    │   └── acs_...-5.log
    └── state
        ├── acs_...-1.log
        ├── ...
        ├── acs_...-1.log
```

To validate that they ran correctly:
```bash
$ cd datausa-acs-bamboo-etl
# If running on a Mac with ARM Processor: Edit the dockerfile and insert the --plaftorm on the FROM line.
$ docker run --rm -d -v $(pwd):/datausa-acs-bamboo-etl --workdir /datausa-acs-bamboo-etl datausa-acs-bamboo-etl:latest bash updates/log-search.sh
$ cat result.txt
# here on the file you'll see all files that have an error. you can run them manually afterwards. If there's an issue, pleas contact us!
```

## Local ingestion test

Configure a postgres database and a monet database using docker. This procedure can be used as a test to run and check locally before doing changes on the databases of the project.


### Start a MonetDB database

```bash
# Create the database
docker run -d \
  --name monetdb-container \
  -e MONETDB_PASSWORD=monetdb \
  -e MONETDB_USERNAME=monetdb \
  -e MDB_CREATE_DBS=datausa \
  -p 50000:50000 \
  monetdb/monetdb

# Create acs Schema
docker exec -it monetdb-container mclient -u monetdb -P monetdb -d datausa -s "CREATE SCHEMA acs;"
```

### Start a PostgreSQL database
```bash
# Create the database
docker run -d \
  --name postgres-datausa \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=datausa_vp \
  -p 5432:5432 \
  postgres        
```

### Create an env.local file


```bash
PYTHONPATH=/datausa-acs-bamboo-etl
DATAUSA_DB_PW=monetdb
DATAUSA_DB_HOST=localhost
BAMBOO_DB_PW=password
BAMBOO_DB_HOST=localhost:5432
API_KEY=<API_KEY>
```

# Questions
If there's a question about this ask me at `nicolas.netz@datawheel.us`
