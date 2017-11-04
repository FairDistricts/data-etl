#! python
# -*- coding: utf-8 -*-
"""
Main schema file and data imports...
"""

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func, PrimaryKeyConstraint
from sqlalchemy.orm import relationship, backref
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
    vote_id = Column(String(64), primary_key=True)
    vote = Column(String(32))
    legislator_id = Column(String(64), primary_key=True)  # TODO: fix with right relationship below
    # legislator_id = relationship(
    #    Legislator,
    #    secondary='legislator_id'
    # )


class Bills(Base):
    __tablename__ = 'bills'
    bill_id = Column(String(128), primary_key=True)
    session = Column(Integer, primary_key=True)
    state = Column(String(64), primary_key=True)
    civic_level = Column(String(128))
    title = Column(String(256))
    subjects = Column(String(512))
    bill_type = Column(String(64))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class BillSponsor(Base):
    __tablename__ = 'sponsors'
    legislator_id = Column(String(64),  primary_key=True)
    bill_id = Column(String(128), primary_key=True)  # TODO: fix with relationship below
    # bill_id = relationship(
    #    Bills,
    #    secondary='bill_id'
    # )
    session = Column(Integer, primary_key=True)
    state = Column(String(32))
    sponsor_type = Column(String(64))


class Roles(Base):
    __tablename__ = 'roles'
    legislator_id = Column(String(64),  primary_key=True)  # TODO: match with other legislator
    session = Column(Integer, primary_key=True)
    state = Column(String(32))
    district = Column(String(32))
    party = Column(String(32))
    committee_ids = Column(String(256))
    committee = Column(String(512))


def default_uri():
    if False:   #  use old database credentials
        return 'mysql+mysqldb://{:}:{:}@{:}:{:}/{:}'.format('atxhackathon', 'atxhackathon',
                            'atxhackathon.chs2sgrlmnkn.us-east-1.rds.amazonaws.com',
                            3306, 'atxhackathon')
    else:
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
