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


# parse
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
3. Then run the parse to ingest new data from the CSV data (in example below).  This
   will parse the first level of an entire directory.  If you provide a file, it will
   parse only the file provided

```
./bin/run_local.sh parse -i data/2017-06-02-tx-csv   (whole directory)
./bin/run_local.sh parse -i data/2017-06-02-tx-csv/tx_bill_actions.csv   (single file)
```

### Where does it run?
As of version `0.2.0`, a conditional `database_type` flag was added to use either a local sqlite
database or the initial group's msyql database.


# server
Assuming you have a legit source of data (see above), you can start a simple rest
server to provide data (and answer simple queries) via simple eve server.

## Running eve server
1. Run the server with proximity to the data file (assuming it's in the current dir)

``./bin/run_local.sh server``

2. Go to your nearest server and point to the endpoint you just created e.g. [http://127.0.0.1:5000](http://localhost:5000).
   With this as the testing end point, Eve will list the known data end points.
3. To query the set of votes (just get a whole list), you can simply request that
   [in your browser](http://localhost:5000/votes) or via curl.  Note that the
   return type will vary based on your request header (e.g. XML or JSON).

``curl "http://localhost:5000/votes" ``

4. Want to slice the data ina different way? Check out the [cool set of examples](http://python-eve.org/features.html
   available in the full fledged python sample, or try a query like the one below,
   which will bills found between two date ranges.

```
curl -g 'http://127.0.0.1:5000/bill?where=created_at%20%3E%20%272017-02-31%2010:22:50%27%20and%20created_at%3C%272017-03-07%2010:22:50%27&max_results=100' (bills created between March 1,2017 and March 7,2017)
```

   Or one that will all look at roles a few ways... Note that if you're not using a
   MongoDB database backend, some functions may not behave exactly as expected according
   to the above documentation.  Instead, you can use `python` based notation, like the queries
   below.

```
curl -g 'http://127.0.0.1:5000/role?where={"party":"Democrat"}&sort=-session'  (Democrat members in latest sesssion - reverse sort)
curl -g 'http://127.0.0.1:5000/role?where={%22district%22:20.0}&max_results=100&pretty' (district 20 roles, all results, pretty json)
curl -g 'http://127.0.0.1:5000/action?where=count_other%3E=50' (count of 'other' votes was > 50)
curl -g 'http://127.0.0.1:5000/action?where=count_yes%3E=100%20and%20count_yes%3C120' (count of 'yes' was between 100 and 120)
curl -g 'http://127.0.0.1:5000/bill?where=created_at%20%3E%20%272017-02-31%2010:22:50%27%20and%20created_at%3C%272017-03-07%2010:22:50%27&max_results=100' (bills created between March 1,2017 and March 7,2017)
```

## Screenshots
Below are two examples of the returned JSON.
1. Returning bills in a time range from the time-bound query above ![bills query](data/images/bill_example.jpg)
2. Querying for recent Democrats from the time-bound query above ![role query](data/images/role_recent_democrat.jpg)
