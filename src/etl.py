from json import load, loads
from os import listdir
import pandas as pd
from re import search
import numpy as np

def get_data():
    '''
    Gets data from the test/testdata directory
    '''
    fp = "test/testdata/test-data.JSON"
    f = open(fp, 'r')
    data = load(f)
    f.close()
    return data

def get_ids():
    fp = "test/testdata/test_ids.csv"
    id_csv = pd.read_csv(fp, skiprows=0)
    drop_cols = id_csv.columns[3:6].to_list() + [id_csv.columns[7]]
    id_csv = id_csv.drop(columns=drop_cols)
    id_csv.columns = ['batch_id', 'sample_id', 'file_type', 'file_id']
    return id_csv