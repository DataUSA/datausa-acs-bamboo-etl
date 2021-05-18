# Analysis Folder

This folder should contain two Python scripts:

* `tables_helper.py`: Has a list of all the ACS table names in the database.
* `build_status.py`: Generates a CSV file with the total amount of rows per year, total rows and total amount of rows per geo level of each table on a remote database.

## Usage

In order to use `build_status.py` you need to:

* Create a Python 3.7 virtual environment and activate it.
* Create an environment variables file and source it, only MonetDB is supported, it should have these:

```
export DB_USER='';
export DB_PW='';
export DB_HOST='';
export DB_NAME='';
```

* Go inside the folder and run the script.