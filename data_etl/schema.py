import os

from sqlalchemy import Column, DateTime, String, Integer, ForeignKey, func
from sqlalchemy.orm import relationship, backref
from sqlalchemy.ext.declarative import declarative_base

import pymysql
pymysql.install_as_MySQLdb()

Base = declarative_base()

class Legislator(Base):
    __tablename__ = 'legislator'
    legislator_id = Column(String(128), primary_key=True)
    first_name = Column(String(128))
    last_name = Column(String(128))
    full_name = Column(String(128))
    civic_level = Column(String(64))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    active = Column(Integer)
    state = Column(String(64))
    image = Column(String(512))
    misc_data = Column(String(512))


class Votes(Base):
    __tablename__ = 'bill_legislative_votes'
    vote_id = Column(String(128), primary_key=True)
    vote = Column(String(32))
    legislator_id = relationship(
        'Legislator',
        secondary='legislator_id'
    )


class Bill(Base):
    __tablename__ = 'bills'
    bill_id = Column(String(128), primary_key=True)
    state = Column(String(64))
    civic_level = Column(String(128))
    title = Column(String(256))
    subjects = Column(String(512))
    bill_type = Column(String(64))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class BillSponsor(Base):
    __tablename__ = 'bill_sponsor'
    legislator_id = Column(String(128), primary_key=True)
    bill_id = relationship(
        'Bill',
        secondary='bill_id'
    )
    session = Column(String(128))
    state = Column(String(64))
    sponsor_type = Column(String(64))


def create_session(db_host, db_user, db_pass, db_port, db_name):
    from sqlalchemy import create_engine
    engine = create_engine('mysql+mysqldb://{:}:{:}@{:}:{:}/{:}'.format(db_user, db_pass, db_host, db_port, db_name), pool_recycle=3600)
    from sqlalchemy.orm import sessionmaker
    Session = sessionmaker(bind=engine)
    Base.metadata.create_all(engine)
    session = Session()
    return session
