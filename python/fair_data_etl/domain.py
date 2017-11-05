#! python
# -*- coding: utf-8 -*-
"""
Main schema file and data imports...
"""

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, UniqueConstraint, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

import pymysql
pymysql.install_as_MySQLdb()

Base = declarative_base()


class Legislator(Base):
    __tablename__ = 'legislator'
    legislator_id = Column(String(64), primary_key=True)
    first_name = Column(String(128))
    last_name = Column(String(128))
    full_name = Column(String(128))
    civic_level = Column(String(64))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    active = Column(Integer)
    state = Column(String(32))
    image = Column(String(512))
    misc_data = Column(String(512))


class Votes(Base):
    __tablename__ = 'votes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    vote_id = Column(String(32))
    vote = Column(String(16))
    legislator_id = Column(String(64), ForeignKey('legislator.legislator_id'))
    legislator = relationship("Legislator")
    __tableargs__ = (UniqueConstraint(vote_id, legislator_id), )


class Bills(Base):
    __tablename__ = 'bills'
    id = Column(Integer, primary_key=True, autoincrement=True)
    bill_id = Column(String(64))
    session = Column(Integer)
    state = Column(String(64))
    civic_level = Column(String(128))
    title = Column(String(256))
    subjects = Column(String(512))
    bill_type = Column(String(64))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    __tableargs__ = (UniqueConstraint(bill_id, session, state), )


class Actions(Base):
    __tablename__ = 'actions'
    id = Column(Integer, primary_key=True, autoincrement=True)
    passage = Column(Boolean)  # passage or other?
    vote_id = Column(String(64), ForeignKey('votes.vote_id'))
    bill_id = Column(String(64), ForeignKey('bills.bill_id'))
    __tableargs__ = (UniqueConstraint(vote_id, bill_id), )
    created_at = Column(DateTime)
    count_yes = Column(Integer)
    count_no = Column(Integer)
    count_other = Column(Integer)
    vote = relationship("Votes")
    bill = relationship("Bills")


class BillSponsor(Base):
    __tablename__ = 'sponsors'
    id = Column(Integer, primary_key=True, autoincrement=True)
    legislator_id = Column(String(64), ForeignKey('legislator.legislator_id'))
    bill_id = Column(String(64), ForeignKey('bills.bill_id'))
    session = Column(Integer)
    state = Column(String(32))
    sponsor_type = Column(String(64))
    legislator = relationship("Legislator")
    bill = relationship("Bills")
    __tableargs__ = (UniqueConstraint(legislator_id, bill_id, session, sponsor_type), )


class Roles(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    legislator_id = Column(String(64), ForeignKey('legislator.legislator_id'))
    session = Column(Integer)
    state = Column(String(32))
    district = Column(String(32))
    party = Column(String(32))
    committee_ids = Column(String(256))
    committee = Column(String(512))
    legislator = relationship("Legislator")
    __tableargs__ = (UniqueConstraint(legislator_id, session), )


def default_uri(database_type, include_dir=None):
    print("Returning database URI for type '{:}'...".format(database_type))
    if database_type == 'msyql':   # use old database credentials
        return 'mysql+mysqldb://{:}:{:}@{:}:{:}/{:}'.format('atxhackathon', 'atxhackathon',
                        'atxhackathon.chs2sgrlmnkn.us-east-1.rds.amazonaws.com',
                        3306, 'atxhackathon')
    elif database_type == 'sqlite':
        if include_dir is not None:
            return 'sqlite:///{:}/fairdata.db'.format(include_dir)
        return 'sqlite:///fairdata.db'


def create_session_uri(db_uri, purge_first=False):
    from sqlalchemy import create_engine
    engine = create_engine(db_uri, pool_recycle=3600)
    from sqlalchemy.orm import sessionmaker
    if purge_first:
        print(" --- Warning, droping dtabase first --- ")
        Base.metadata.drop_all(engine)   # all tables are deleted
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    session = Session()
    return session
