#!/usr/bin/env python

import sys
import os
import json

sys.path.insert(0, 'src')

from etl import get_data, get_ids
from chem_feature import *
from action_feature import *
from link_feature import *
from query_feature import *

def main(targets):
    '''
    Runs the main project pipeline on the given targets.
    Targets are "data", "features", "graph"
    
    'main' should run the targets in order:
    'data' -> 'features' -> 'graph'
    '''
    if 'test' in targets:
        targets = ['data', 'features', 'graph']
        
    if 'data' in targets:
        data = get_data()
        file_ids = get_ids()
        
    if 'features' in targets:
        # creates and saves to_csv the chemical tables
        save_chem_csvs(data)
        # creates and saves to_csv the action tables, which returns a list of the dataframes
        action_dfs = save_action_csvs(data)
        # takes in the previously created action tables and creates + saves to_csv the link tables.
        save_link_csvs(action_dfs)
    
    if 'graph' in targets:
        samples = file_ids['sample_id'].unique()
        ids = []
        for sample in samples:
            sample_links = file_ids[file_ids['sample_id']==sample]
            temp_ids = []
            for i in [1, 0, 2]:
                temp_ids.append(sample_links.iloc[i]['file_id'])
            ids.append(temp_ids)
        queries = []
        for s in ids:
            queries.append(query_maker(s[0], s[1], s[2]))
        query_file(queries_list)
        
        os.system('docker run --name neo4j_session -p7474:7474 -p7687:7687 -d --env NEO4J_AUTH=neo4j/test neo4j:latest')
        
        os.system('docker cp output.cypher neo4j_session:/graph_output.cypher')
        
    return

if __name__ == '__main__':
    targets = sys.argv[1:]
    main(targets)