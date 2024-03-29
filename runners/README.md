# ACS Bash Runner
To avoid running every pipeline by itself and taking advantage from the standarization of the codebase, the file `/runners/runner.sh` allows to run all ACS pipelines in one command, and create log files for each pipeline execution, so that the success of a pipeline run can be asserted.

## How to use the runner script?
### Some things to consider
* It's required to have a *python virtual enviroment* with all the required libraries already created.
* It's required to have a *.env* file such that it includes:

```bash
export API_KEY='';
export DATAUSA_DB_PW='password';
export DATAUSA_DB_HOST='1.2.3.4';
export PYTHONPATH=$PYTHONPATH:/path/to/datausa/datausa-acs-bamboo-etl;
export BAMBOO_DB_PW='password';
export BAMBOO_DB_HOST='1.2.3.4';
```

### Usage
The script takes three parameters:
1. DATAUSA_PATH: Path in filesystem to the repository. ex. /code/datausa/datausa-acs-bamboo-etl
2. VENV_PATH: Path in filesystem to venv. ex. /code/datausa/datausa-acs-bamboo-etl/venv
3. SERVERS: Servers to point to. ex. postgres-zcube or monet-backend
4. YEAR: Year to be ingested. ex. 2021.
5. ESTIMATES: Estimate to be ingested. Ex. 5 or 1.

To run the script, create a screen session, and go to the repository. Then execute the script:
```bash
$ screen -S datausa
$ cd /path/to/datausa-acs-bamboo-etl
# ingest 2021 to postgres
$ bash runners/runner.sh /home/deploy/datausa-acs-bamboo-etl/ /home/deploy/datausa-acs-bamboo-etl/venv postgres-zcube 2022 5
# The script should start. You should see some terminal output as:

INFO:bamboo_lib.logger:Received parameter with key=year and value=2021
INFO:bamboo_lib.logger:Received parameter with key=estimate and value=1
INFO:bamboo_lib.logger:Received parameter with key=server and value=postgres-zcube
INFO:bamboo_lib.logger:Downloading 2021: us from API...
INFO:bamboo_lib.logger:Downloading 2021: us from API...
# You can detach the screen session by using: Ctrl + a + d
# You can quit the terminal and log back using:
$ screen -ls
There is a screen on:
        2010743.datausa (07/24/2023 08:18:56 PM)        (Detached)
1 Socket in /run/screen/S-netz.
$ screen -r datausa
# Now you should be back
```

### Data checks
To confirm that the ingestion process was succesful, you need to check all logs located on `/runners/logs/*`. Those are separated in folders, by server, acs estimate and year:

```bash
├── logs
│   ├── monet-backend
│   │   ├── 1
│   │   │   └── 2021
│   │   └── 5
│   │       └── 2021
│   └── postgres-zcube
│       ├── 1
│       │   └── 2021
│       └── 5
│           └── 2021
```

You can copy these files to your file system using `scp` and check them there or you can use the VS-Code SSH Extension to navigate those files with an UI directly from the server.


# Questions
If there's a question about this ask me at `nicolas.netz@datawheel.us`
