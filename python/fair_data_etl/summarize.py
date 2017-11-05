#! python
# -*- coding: utf-8 -*-
"""
Wrapper for data parsing of various data stores
"""

import sys
import re
import time
from math import floor
from operator import itemgetter

from stemming.porter2 import stem

from fair_data_etl import domain


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


def summarize_words(config, session):
    # always drop the table that we're going to work on?
    domain.DistrictWords.__table__.drop(session.engine)
    domain.DistrictWords.__table__.create(session.engine)
    domain.Words.__table__.drop(session.engine)
    domain.Words.__table__.create(session.engine)

    time_start = time.time()
    print("Extracting words from bill titles in database...")

    # order of operations is a little different here because we want to pre-filter
    #   to remove high- and low-frequency words...
    dict_words = {}
    reNormalize = re.compile(r"[^0-9a-z]+")
    for row_bill in session.query(domain.Bills).all():
        raw_words = reNormalize.sub(' ', row_bill.title.lower()).split(" ")  # gathered words
        stem_words = [stem(word) for word in raw_words]
        for i in range(len(raw_words)):
            if stem_words[i] not in dict_words:
                dict_words[stem_words[i]] = {'words': [], 'count': 0, 'stem': stem_words[i]}
            dict_words[stem_words[i]]['words'].append(raw_words[i])
            dict_words[stem_words[i]]['count'] += 1
    # now strip down to a list
    list_stems = list(dict_words.values())
    # sort by count
    list_stems = sorted(list_stems, key=itemgetter('count'))
    # truncate top/buttom 5% of words (standard trick for lingual processing)
    num_truncate = int(floor(len(list_stems) * 0.05))
    if len(list_stems) > 3 * num_truncate:  # just size safety
        list_stems = list_stems[num_truncate:-num_truncate]
    # finally add new list items and restore the dict process
    dict_words = {}
    for s in list_stems:
        new_id = len(dict_words) + 1
        for w in list(set(s['words'])):
            ormAdd = domain.Words(tag=w, tag_stem=s['stem'], word_id=new_id)
            dict_words[w] = new_id  # don't care about freq, can always recompute
            session.add(ormAdd)
    session.commit()
    print("...done, trimmed {:} words for a total dictionary size of {:}".format(num_truncate, len(dict_words)))

    # want to query all bills language
    #   summarize yearly (by session) and by precinct
    #      summarize keyword + votes FOR, votes AGAINST

    bill_first = session.query(domain.Bills.session, domain.Bills.created_at).order_by(domain.Bills.created_at.asc()).first()
    bill_last = session.query(domain.Bills.session, domain.Bills.updated_at).order_by(domain.Bills.created_at.desc()).first()
    numRecord = 0
    print("Executing word summary for session {:} to session {:}".format(bill_first, bill_last))

    dict_votes = {}
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
            raw_words = reNormalize.sub(' ', row_bill.Bills.title.lower()).split(" ")  # gathered words
            list_words = [dict_words[s] for s in raw_words if s in dict_words]  # translate to number if not pruned
            for subject in list_words:  # iterate throuhg subjects to create markers
                dict_votes[subject] = {}
            # print(list_subjects)
            for row_vote in session.query(domain.Votes, domain.Legislator, domain.Roles).filter(
                                  domain.Votes.vote_id == row_bill.Actions.vote_id).filter(
                                  domain.Legislator.legislator_id == domain.Votes.legislator_id).filter(
                                  domain.Roles.session == session_id).filter(
                                  domain.Roles.legislator_id == domain.Legislator.legislator_id).all():
                for subject in list_words:  # iterate throuhg subjects to create markers
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
                    ormAdd = domain.DistrictWords(word_id=subject, district=district,
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


def main(config={}):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--database_type', type=str, default='sqlite', help='specify the database backend', choices=['sqlite', 'mysql'])
    parser.add_argument('-m', '--summary_mode', type=str, default='all', help='specify the summary mode to use', choices=['all', 'word', 'subject'])

    config.update(vars(parser.parse_args()))  # pargs, unparsed = parser.parse_known_args()

    # create the session for interaction
    session = domain.create_session_uri(domain.default_uri(config['database_type']), False)
    # proceed to summarize data
    if not config['summary_mode'] == "word":
        summarize_subjects(config, session)
    if not config['summary_mode'] == "subject":
        summarize_words(config, session)


if __name__ == '__main__':
    main()
