#! python
# -*- coding: utf-8 -*-
"""
In place data server using SQL schema for easy rest operations using Eve
"""
from eve import Eve
from eve_sqlalchemy import SQL
from eve_sqlalchemy.config import DomainConfig, ResourceConfig
from eve_sqlalchemy.validation import ValidatorSQL

from fair_data_etl.domain import default_uri, Legislator, Votes, Bills, BillSponsor, Roles, Actions, Base

import os

def main(config_args={}):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--database_type', type=str, default='sqlite', help='specify the database backend', choices=['sqlite', 'mysql'])

    config_args.update(vars(parser.parse_args()))  # pargs, unparsed = parser.parse_known_args()

    cwd = os.getcwd()
    print("Using current working directory...'{:}'".format(cwd))
    SETTINGS = {
        'DEBUG': True,
        'DATE_FORMAT': '%Y-%m-%d %H:%M:%S',  # 2017-02-01 10:00:00
        'PAGINATION_LIMIT': 250,
        'SQLALCHEMY_DATABASE_URI': default_uri(config_args['database_type'], cwd),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JSON_ARGUMENT': 'callback',
        'RESOURCE_METHODS': ['GET'],
        'DOMAIN': DomainConfig({
           'legislator': ResourceConfig(Legislator),
           'vote': ResourceConfig(Votes),
           'bill': ResourceConfig(Bills),
           'sponsor': ResourceConfig(BillSponsor),
           'role': ResourceConfig(Roles),
           'action': ResourceConfig(Actions)
        }).render()
    }

    app = Eve(auth=None, settings=SETTINGS, validator=ValidatorSQL, data=SQL)

    # bind SQLAlchemy
    db = app.data.driver
    Base.metadata.bind = db.engine
    db.Model = Base
    db.create_all()

    # using reloader will destroy the in-memory sqlite db
    app.run(debug=True, use_reloader=False)


if __name__ == '__main__':
    main()
