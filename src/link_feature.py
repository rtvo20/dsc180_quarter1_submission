from json import load, loads
from os import listdir
import pandas as pd
from re import search
import numpy as np

def goes_into_links(dissolve_rows):
    """
    Helper method to create links for chemical nodes that "go into" a dissolve node.
        AKA the "GOES_INTO" links
    :param dissolve_rows: From an action table, takes in the rows of the table where dissolve
        steps are involved. For this batch, this is at the beginning steps of the action table
    """
    # step_id, action(link), chemical_from, step_to, chemical_to, step_from, sample_id, batch_id
    row_template = [0, 'GOES_INTO', 0, 0, np.nan, np.nan]
    links = []
    for i in range(dissolve_rows.shape[0]):
        row = dissolve_rows.iloc[i]
        link = row_template.copy()
        link[0] = row['step_id']
        link[2] = row['chemical_from']
        link[3] = link[2]
        links.append(link)
    return links

def output_links(dissolve_rows):
    """
    Helper method to create the OUTPUTS links from the initial solutes and solvents used
    :param dissolve_rows: From an action table, takes in the rows of the table where dissolve
        steps are involved. For this batch, this is at the beginning steps of the action table
    """
    row_template = [0, 'OUTPUTS', np.nan, np.nan, 0, 0]
    links = []
    mix_step = dissolve_rows.iloc[-1]['step_id']+1
    prev_step = dissolve_rows.iloc[-1]['step_id']
    for i in range(dissolve_rows.shape[0]):
        row = dissolve_rows.iloc[i]
        link = row_template.copy()
        link[0] = prev_step+1
        prev_step +=1
        link[4] = mix_step
        link[5] = row['step_id']
        links.append(link)
    return links

def next_func(other_steps, step_num):
    # step_id, action, chemical_from, step_to, chemical_to, step_from
    row_template = [0, 'NEXT', np.nan, np.nan, np.nan, 0]
    rows = []
    step_id = step_num
    for i in range(other_steps.shape[0]):
        step_to = other_steps.iloc[i]['step_id']
        row = row_template.copy()
        row[0] = step_id
        row[3] = step_to
        row[-1] = row[3] - 2
        rows.append(row)
        step_id += 2
    return rows

def link_table(action_table, sample_id, batch_id):
    dissolve_rows = action_table[action_table['action'] == 'dissolve']
    go_into = goes_into_links(dissolve_rows)
    outputs = output_links(dissolve_rows)
    
    next_link_step = outputs[-1][0] + 3
    
    mix1_into_drop = [next_link_step, 'GOES_INTO', outputs[-1][4], outputs[-1][0]+1, np.nan, np.nan]
    
    next_link_step += 1 
    
    first_drop_step_id = action_table[action_table['action']=='drop'].iloc[0]['step_id']
    second_drop_step_id = first_drop_step_id + 1
    mix2_chem_id = mix1_into_drop[2] + 2
    
    mix1_to_mix2 = [next_link_step, 'NEXT', np.nan, np.nan, mix2_chem_id, first_drop_step_id]
    
    mix_antisolvent = [action_table.iloc[-1]['step_id']+4, 'GOES_INTO', mix2_chem_id-1, second_drop_step_id, np.nan, np.nan]
    
    next_link_step += 2
    drop_to_mix2 = [next_link_step, 'NEXT', np.nan, np.nan, mix2_chem_id, second_drop_step_id]
    
    spin_step_id = action_table[action_table['action']=='spin'].iloc[0]['step_id']
    mix2_to_spin = [next_link_step, 'GOES_INTO', mix2_chem_id, spin_step_id, np.nan, np.nan]
    
    next_steps = action_table[action_table['step_id']>spin_step_id]
    
    next_rows = next_func(next_steps, next_link_step+2)

    res = go_into + outputs + [mix1_into_drop] + [mix1_to_mix2] + [mix_antisolvent] + [drop_to_mix2] + [mix2_to_spin] + next_rows 
    
    for i in res:
        i.append(sample_id)
        i.append(batch_id)
    return res

def save_link_csvs(action_dfs):
    link_cols = ['step_id','action','chemical_from','step_to','chemical_to','step_from','sample_id','batch_id']
    for act in action_dfs:
        batch_id = act.iloc[0]['batch_id']
        df = pd.DataFrame(link_table(act, act.iloc[0]['sample_id'], batch_id), columns=link_cols)
        df = df.astype({'chemical_from':'Int64', 'step_to':'Int64', 'chemical_to':'Int64', 'step_from':'Int64'})
        fname = batch_id + '_' + act.iloc[0]['sample_id'] + '_link.csv'
        df.to_csv(fname, index=False)
    return
        



