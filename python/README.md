# DATA-ETL
Utilities for importing and manaing data from different sources.

In the python library here, you'll find a mix of simple commands that don't
require you to install the library to your local [pip](https://en.wikipedia.org/wiki/Pip_(package_manager))
or [conda](https://conda.io/docs/) local installation,
but that might be a good idea.

Generally the execution pattern will be something like this without installing:

``./bin/run_local.sh <run_mode> <arguments>``

... or something like this for a run after local installation (e.g. ``pip install .``):

``run_fair_data_<run_mode> <arguments>``

* **parse** - allows you to parse new data
* **server** - allows you to serve REST-based data queries from the database backend via [Eve](http://python-eve.org/index.html)


# parsing
You can parse and ingest new data (as of `0.2.0` just from *OpenStates*) from
a few locations such that the data will be available in an MySQL or sqlite database.

## Using precomputed data
Althogh it may not be the best way to shuttle around data, you can find a
pre-computed [sqlite database](data/fairdata.db.gz).  Don't forget, to use this
file in your own instance, you'll need to `gunzip` it first and then move
it to the base directory of the python repo.


## Importing new data example
1. First, install the package to get all of the dependencies...

``pip install data_etl``

2. Optionally, download the data from [OpenStates](https://openstates.org/downloads/)
3. Then run the parse to ingest new data from the CSV data (in example below)

``./bin/run_local.sh parse -i data/2017-06-02-tx-csv``

### Where does it run?
As of version `0.2.0`, a conditional `database_type` flag was added to use either a local sqlite
database or the initial group's msyql database.

