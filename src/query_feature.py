from json import load, loads
from os import listdir
import pandas as pd
from re import search
import numpy as np

def create_chem_nodes(file_id):
    query_start = "LOAD CSV WITH HEADERS FROM "
    url = "\"https://drive.google.com/uc?export=download&id={}\" "
    url = url.format(file_id)
    query = "AS row CREATE (c:Chemical {chemical_id: row['chemical_id'], batch_id: row['batch_id'], \
content: row['content'], molarity: row['molarity'], concentration: row['concentration'], \
volume: row['volume'], type: row['type'], sample_id: row['sample_id']});"
    return query_start + url + query

def create_action_nodes(file_id):
    query_start = "LOAD CSV WITH HEADERS FROM "
    url = "\"https://drive.google.com/uc?export=download&id={}\" "
    url = url.format(file_id)
    query = "AS row CREATE (a:Action {step_id: row['step_id'], action: row['action'], sample_id: row['sample_id'], \
batch_id: row['batch_id'], content: row['content'], height:row['drop_height'], spin_acc:row['spin_acc']});"
    return query_start + url + query

def create_links(file_id):
    query_start = "LOAD CSV WITH HEADERS FROM "
    url = "\"https://drive.google.com/uc?export=download&id={}\" "
    url = url.format(file_id)
    
    query_1 = "AS row MATCH (c:Chemical {chemical_id: row['chemical_from'], sample_id: row['sample_id'], \
batch_id: row['batch_id']}), (a:Action {step_id:row['step_to'], sample_id: row['sample_id'], \
batch_id: row['batch_id']}) CREATE (c)-[:GOES_INTO]->(a);"
    
    query_2 = "AS row MATCH (a1:Action {action: 'dissolve', step_id: row['step_from'], sample_id: row['sample_id'], \
batch_id: row['batch_id']}),(c1:Chemical {chemical_id:row['chemical_to'], sample_id: row['sample_id'], \
batch_id: row['batch_id']}) CREATE (a1)-[:OUTPUTS]->(c1);"
    
    query_3 = "AS row MATCH (a3:Action {action:'drop',step_id: row['step_from'], sample_id: row['sample_id'], \
batch_id: row['batch_id']}),(c4:Chemical {chemical_id:row['chemical_to'], sample_id: row['sample_id'], \
batch_id: row['batch_id']}) CREATE (a3)-[:NEXT]->(c4);"
    
    query_4 = "AS row MATCH (a3:Action {step_id: row['step_from'], sample_id: row['sample_id'], \
batch_id: row['batch_id']}),(a4:Action {step_id:row['step_to'], sample_id: row['sample_id'], \
batch_id: row['batch_id']}) CREATE (a3)-[:NEXT]->(a4);"
    
    query_start = query_start + url
    queries = []
    for i in [query_1, query_2, query_3, query_4]:
        query_str = query_start + i
        queries.append(query_str)
    
    return queries

def query_maker(chem_fileid, action_fileid, link_fileid):
    """
    Calls the other query functions in this one function, given the necessary file ids
    """
    queries = []
    queries.append(create_chem_nodes(chem_fileid))
    queries.append(create_action_nodes(action_fileid))
    
    queries = queries + create_links(link_fileid)
    return queries

def query_file(queries_list):
    output = open('output.cypher', 'w')
    for q in queries_list:
        for query in q:
            output.write(query)
    output.close()
    return
