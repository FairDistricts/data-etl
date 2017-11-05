#! python
# -*- coding: utf-8 -*-
"""
In place data server using SQL schema for easy rest operations using Eve
"""
from eve import Eve
from eve_sqlalchemy import SQL
from eve_sqlalchemy.config import DomainConfig, ResourceConfig
from eve_sqlalchemy.validation import ValidatorSQL
from sqlalchemy.ext.declarative import declarative_base

from fair_data_etl.domain import default_uri, Legislator, Votes, Bills, BillSponsor, Roles, Actions

Base = declarative_base()


def main(config_args={}):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--database_type', type=str, default='sqlite', help='specify the database backend', choices=['sqlite', 'mysql'])

    config_args.update(vars(parser.parse_args()))  # pargs, unparsed = parser.parse_known_args()

    SETTINGS = {
        'DEBUG': True,
        'SQLALCHEMY_DATABASE_URI': default_uri(config_args['database_type']),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'RESOURCE_METHODS': ['GET'],
        'DOMAIN': DomainConfig({
           'legislator': ResourceConfig(Legislator),
           'votes': ResourceConfig(Votes),
           'bills': ResourceConfig(Bills),
           'sponsors': ResourceConfig(BillSponsor),
           'roles': ResourceConfig(Roles),
           'actions': ResourceConfig(Actions)
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
