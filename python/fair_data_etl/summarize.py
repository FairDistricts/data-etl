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

from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound
import datetime

def summarize_subjects(config, session):
    # always drop the table that we're going to work on?
    domain.DistrictSubjects.__table__.drop(session.engine)
    domain.DistrictSubjects.__table__.create(session.engine)
    domain.Subjects.__table__.drop(session.engine)
    domain.Subjects.__table__.create(session.engine)

    bill_first = session.query(domain.Bills.session, domain.Bills.created_at).order_by(domain.Bills.created_at.asc()).first()
    bill_last = session.query(domain.Bills.session, domain.Bills.updated_at).order_by(domain.Bills.created_at.desc()).first()
    numRecord = 0
    print("Executing subject summary for session {:} to session {:}".format(bill_first, bill_last))

    # want to query all bills language
    #   summarize yearly (by session) and by precinct
    #      summarize keyword + votes FOR, votes AGAINST

    dict_subjects = {}
    time_start = time.time()
    for session_id in range(bill_first[0], bill_last[0] + 1):  # loop through all sessions
        dict_votes = {}
        create_date = None
        update_date = None
        for row_bill in session.query(domain.Bills, domain.Actions).filter(
                          domain.Bills.session == session_id).filter(
                          domain.Actions.bill_id == domain.Bills.bill_id).filter(
                          domain.Actions.passage == True).all():
            if create_date is None:  # save the first create date
                create_date = row_bill.Bills.created_at
            update_date = row_bill.Bills.updated_at  # always update last date
            raw_subjects = row_bill.Bills.subjects.split("|")  # gathered subjects
            for subject in raw_subjects:
                if subject not in dict_subjects:
                    dict_subjects[subject] = len(dict_subjects) + 1
                    ormAdd = domain.Subjects(subject_id=dict_subjects[subject], tag=subject)
                    session.add(ormAdd)

            list_subjects = [dict_subjects[s] for s in raw_subjects]  # translate to number
            for subject in list_subjects:  # iterate throuhg subjects to create markers
                dict_votes[subject] = {}
            # print(list_subjects)
            for row_vote in session.query(domain.Votes, domain.Legislator, domain.Roles).filter(
                                  domain.Votes.vote_id == row_bill.Actions.vote_id).filter(
                                  domain.Legislator.legislator_id == domain.Votes.legislator_id).filter(
                                  domain.Roles.session == session_id).filter(
                                  domain.Roles.legislator_id == domain.Legislator.legislator_id).all():
                for subject in list_subjects:  # iterate throuhg subjects to create markers
                    if row_vote.Roles.district not in dict_votes[subject]:  # validate district in subject
                        dict_votes[subject][row_vote.Roles.district] = {}
                    if row_vote.Votes.vote not in dict_votes[subject][row_vote.Roles.district]:  # check to validate vote seen
                        dict_votes[subject][row_vote.Roles.district][row_vote.Votes.vote] = 0
                    dict_votes[subject][row_vote.Roles.district][row_vote.Votes.vote] += 1  # tally new vote
            # print(dict_votes)
        # now that we have accumulated everything for a session
        session.commit()  # push all vocab to disk first
        for subject in dict_votes:
            for district in dict_votes[subject]:
                for vote in dict_votes[subject][district]:
                    count_yes = dict_votes[subject][district]['yes'] if 'yes' in dict_votes[subject][district] else 0
                    count_no = dict_votes[subject][district]['no'] if 'no' in dict_votes[subject][district] else 0
                    count_other = dict_votes[subject][district]['other'] if 'other' in dict_votes[subject][district] else 0
                    ormAdd = domain.DistrictSubjects(subject_id=subject, district=district,
                                                      session=session_id, state=row_vote.Legislator.state,
                                                      count_yes=count_yes, count_no=count_no, count_other=count_other,
                                                      created_at=create_date, updated_at=update_date)
                    session.add(ormAdd)
                    if (numRecord % 1000) == 0:  # occasionally commit to database
                        sys.stdout.write("{:} ".format(numRecord))
                        sys.stdout.flush()
                        session.commit()
                    numRecord += 1
        print("... completed session {:}...".format(session_id))
    session.commit()
    print("... done ({:}s)".format(time.time() - time_start))

    # repeat summary for both 'subjects' and title
    #   for title, perform some keyword aggregation and trimming for top/bottom

    # try to produce a model that predicts what keywords map to what categories?

    # DistrictWords, DistrictSubjects






def main(config={}):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--database_type', type=str, default='sqlite', help='specify the database backend', choices=['sqlite', 'mysql'])

    config.update(vars(parser.parse_args()))  # pargs, unparsed = parser.parse_known_args()

    # create the session for interaction
    session = domain.create_session_uri(domain.default_uri(config['database_type']), False)
    # proceed to summarize data
    summarize_subjects(config, session)


if __name__ == '__main__':
    main()
