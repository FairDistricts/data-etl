# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

# extract __version__ from version file. importing will lead to install failures
setup_dir = os.path.dirname(__file__)
with open(os.path.join(setup_dir, 'fair_data_etl', '_version.py')) as file:
    globals_dict = dict()
    exec(file.read(), globals_dict)
    __version__ = globals_dict['__version__']


setup(
    name = globals_dict['MODEL_NAME'],
    version = __version__,
    packages = find_packages(),
    author = "Eric Z",
    author_email = "ezavesky",
    description = ("Data ETL for voting records for history and object discovery"),
    long_description = ("Data ETL for voting records for history and object discovery"),
    license = "Apache",
    #package_data={globals_dict['MODEL_NAME']:['data/*']},
    scripts=['bin/run_fair_data_server.py', 'bin/run_fair_data_parse.py'],
    setup_requires=['pytest-runner'],
    entry_points="""
    [console_scripts]
    """,
    #setup_requires=['pytest-runner'],
    install_requires=['numpy', 'sqlalchemy', 'Eve-SQLAlchemy',
                      'pymysql', 'sqlite', 'eve_sqlalchemy',
                      'sklearn'],
    tests_require=['pytest',
                   'pexpect'],
    include_package_data=True,
    )
