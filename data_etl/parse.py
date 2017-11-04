#! python
# -*- coding: utf-8 -*-
"""
Wrapper for image emotion classification task
"""

import os.path
import sys

import numpy as np
import pandas as pd

from . import schema

def main(config={}):
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, default='', help='Absolute path to input file')
    parser.add_argument('-t', '--data_type', type=str, default='csv', help='specify the type of input data', choices=['csv', 'json'])
    parser.add_argument('-s', '--data_source', type=str, default='openstate', help='specify the source of the data (for parsing)', choices=['openstate'])
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

    session = schema.create_session(db_user='atxhackathon', db_pass='atxhackathon',
                         db_host='atxhackathon.chs2sgrlmnkn.us-east-1.rds.amazonaws.com',
                         db_port=3306, db_name='atxhackathon')



    #print("Loading raw samples...")
    #rawDf = pd.read_csv(config['input'], delimiter=",")




if __name__ == '__main__':
    main()
