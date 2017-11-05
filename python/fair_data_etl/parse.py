#! python
# -*- coding: utf-8 -*-
"""
Wrapper for data parsing of various data stores
"""

import os.path
import sys
import re
import time
import random

from fair_data_etl import domain
import pandas as pd

DEFAULT_BILL_STATE = 'tx'
DEFAULT_BILL_CIVIC = 'unknown'


def parse_csv(config, session):
    # walk through import of CSV files... should we do something else later?
    from os import listdir
    from os.path import isfile, join

    reBill = re.compile(r"_bills.csv$")
    reVotes = re.compile(r"_bill_legislator_votes.csv$")
    reLegislator = re.compile(r"_legislators.csv$")
    reSponsors = re.compile(r"_bill_sponspors.csv$")
    reRoles = re.compile(r"_legislator_roles.csv$")
    reActions = re.compile(r"_bill_votes.csv$")
    rePassage = re.compile(r"passage")

    # helper function to map from dataframe of bills to database object
    def map_bill(df_row):
        return domain.Bills(bill_id=df_row['bill_id'], state=DEFAULT_BILL_STATE,
                            civic_level=DEFAULT_BILL_CIVIC, title=df_row['title'],
                            subjects=df_row['subjects'], created_at=df_row['created_at'],
                            bill_type=df_row['type'], updated_at=df_row['updated_at'],
                            session=df_row['session'])

    # helper function to map from dataframe of legislators to database object
    def map_legislator(df_row):
        return domain.Legislator(legislator_id=df_row['leg_id'], first_name=df_row['first_name'],
                                 full_name=df_row['full_name'], last_name=df_row['last_name'],
                                 civic_level=DEFAULT_BILL_CIVIC, active=(0 if df_row['active'] == "FALSE" else 1),
                                 subjects=df_row['subjects'], created_at=df_row['created_at'],
                                 image=df_row['photo_url'], misc_data="")

    # helper function to map from dataframe of votes to database object
    def map_votes(df_row):
        return domain.Votes(vote_id=df_row['vote_id'], vote=df_row['vote'],
                            legislator_id=df_row['leg_id'])

    # helper function to map from dataframe of sponsors to database object
    def map_sponsor(df_row):
        return domain.BillSponsor(legislator_id=df_row['leg_id'], bill_id=df_row['bill_id'],
                                  session=df_row['session'], state=df_row['state'],
                                  sponsor_type=df_row['type'])

    # helper function to map from dataframe of legislators to database object
    def map_role(df_row):
        return domain.Roles(legislator_id=df_row['leg_id'], district=df_row['district'],
                            session=df_row['term'], state=df_row['state'],
                            party=df_row['party'], committee_ids=df_row['committee_ids'],
                            committee=df_row['committees'])

    # helper function to map from dataframe of legislators to database object
    def map_actions(df_row):
        return domain.Actions(vote_id=df_row['vote_id'], bill_id=df_row['bill_id'],
                              created_at=df_row['date'], count_yes=df_row['yes_count'],
                              count_no=df_row['no_count'], count_other=df_row['other_count'],
                              passage=(rePassage.search(df_row['motion']) is not None or
                                       rePassage.search(df_row['type']) is not None))

    # TBD>: do something with other data?

    numFiles = 0
    listFiles = [config['input']]
    if not isfile(config['input']):
        listFiles = [join(config['input'], f) for f in listdir(config['input'])]
    for path_full in listFiles:  # recurse
        print("Attempting to load/parse '{:}'...".format(path_full))
        if isfile(path_full):  # if it's a file
            targetFunc = None

            time_start = time.time()

            df = pd.read_csv(path_full)
            drop_na = True

            for col in ['created_at', 'updated_at', 'date']:
                if col in df:
                    df[col] = pd.to_datetime(df[col])

            if numFiles == 0:
                print(df[:5])  # print some example of the data, but not all...
            if reBill.search(path_full) is not None:  # parse bills
                targetFunc = map_bill
            elif reVotes.search(path_full) is not None:  # parse votes
                targetFunc = map_votes
            elif reLegislator.search(path_full) is not None:  # parse legislator
                targetFunc = map_legislator
            elif reSponsors.search(path_full) is not None:
                targetFunc = map_sponsor
            elif reActions.search(path_full) is not None:
                targetFunc = map_actions
            elif reRoles.search(path_full) is not None:
                df_concat = None
                drop_na = False
                df.fillna("", inplace=True)  # fill bad values with empty string
                print("Flattening committees for legislator role ({:} rows)...".format(len(df)))
                for gname, gset in df.groupby(['leg_id', 'term', 'state']):  # flatten comittees
                    df_new = pd.DataFrame([df.ix[gset.index[0]]])
                    df_new['committee_ids'] = "|".join(list(gset['committee_id']))
                    df_new['committees'] = "|".join(list(gset['committee']))
                    if df_concat is None:
                        df_concat = df_new
                    else:
                        df_concat = df_concat.append(df_new, ignore_index=True)
                targetFunc = map_role
                df = df_concat

            if drop_na:
                df.dropna(axis=0, how='any', inplace=True)  # drop any row that has a bad value
                # df.fillna("(unknown {:})".format(int(random.random()*1000000)), inplace=True)

            if targetFunc is None:
                print("Unknown CSV parsing data... '{:}', skipping".format(path_full))
            else:
                # pass through each row in the dataframe
                for i, r in df.iterrows():
                    ormAdd = targetFunc(r)
                    session.add(ormAdd)
                    if (i % 1000) == 0:  # occasionally commit to database
                        sys.stdout.write("{:} ".format(i))
                        sys.stdout.flush()
                        session.commit()
                session.commit()
                print("... done {:}".format(time.time() - time_start))
                numFiles += 1
    print("All done parsing {:} files...".format(numFiles))


def main(config={}):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, default='', help='Absolute path to input file')
    parser.add_argument('-t', '--data_type', type=str, default='csv', help='specify the type of input data', choices=['csv', 'json'])
    parser.add_argument('-s', '--data_source', type=str, default='openstate', help='specify the source of the data (for parsing)', choices=['openstate'])
    parser.add_argument('-k', '--keep_db', default=False, action='store_true', help='do NOT purge all of the data on import')
    parser.add_argument('-d', '--database_type', type=str, default='sqlite', help='specify the database backend', choices=['sqlite', 'mysql'])

    config.update(vars(parser.parse_args()))  # pargs, unparsed = parser.parse_known_args()

    if not os.path.exists(config['input']):
        print("The target input '{:}' was not found, please check input arguments.".format(config['input']))
        sys.exit(-1)
    if not config['data_source'] == 'openstate':
        print("Sorry, the provided data source {:} is not known.".format(config['data_source']))
        sys.exit(-1)
    if not config['data_type'] == 'csv':
        print("Sorry, the provided data type {:} is not known.".format(config['data_type']))
        sys.exit(-1)

    # TODO: avoid deleting all of the data on load!

    # create the session for interaciton
    session = domain.create_session_uri(domain.default_uri(config['database_type']), not config['keep_db'])
    # proceed to ingest data
    parse_csv(config, session)


if __name__ == '__main__':
    main()
