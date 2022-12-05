from json import load, loads
from os import listdir
import pandas as pd
from re import search
import numpy as np

def dissolve_helper(drop_list):
    """
    Helper method to get the dissolve action steps for the action_table function from drop 
    step(s)
    
    :param drop_list: Takes in the worklist with drop information, e.g:
        data['samples']['sample0']['worklist'][1]
        
    :return: Returns a list of lists, where each list is a row in the action dataframe/csv
        associated with a "dissolve" action.
    """
    # get the drop-step information, where the chemicals involved in the dissolve step are 
    # stored
    drop_steps = drop_list['details']['drops']
    
    # row template, step_id, action, chemical_from, followed by NaNs
    row_template = [0, 'dissolve', 0] + [np.nan]*13
    
    # number of solutes and solvents to be mixed for the drop step.
    # For this particular batch, there are either 6 or 7 solutes used along with 2 solvents,
    # totaling 8-9 chemicals per sample. This determines the maximum chemical id (for the 
    # dissolve steps)
    num_chems = len(drop_steps[0]['solution']['solutes'].split('_')) + \
    len(drop_steps[0]['solution']['solvent'].split('_'))
    
    # append each dissolve step to the actions list and return
    actions = []
    for i in range(1, num_chems+1):
        chem_row = row_template.copy()
        chem_row[0] = i
        chem_row[2] = i
        actions.append(chem_row)
    return actions

def drop_helper(drop_list, drop_step_num):
    """
    Helper method to retrieve drop info from a drop list.
    
    :drop_list: the json object containing the drop information.
    drop_step_num: the step number to start from, based on the step from the main function.
    :return: for each drop step, returns the row associated, including step_ids and drop 
        experiment variables: e.g. air_gap, blow_out, drop_height, etc.
    """
    # get drop list info
    drop_list = drop_list['details']['drops']
    
    # create drop step row template
    row_template = [0, 'drop', 0]
    
    drop_rows = []
    i = 1
    # for each drop step in the drop_list:
    for drop in drop_list:
        # get the information for the following drop-step variables and fill in the step
        # information, then append to the list of rows
        air_gap = drop['air_gap']
        blow_out = drop['blow_out']
        drop_height = drop['height']
        drop_rate = drop['rate']
        drop_row = row_template.copy()
        drop_row[0] = drop_step_num*2 + i
        drop_row[2] = drop_step_num + i
        drop_info = [air_gap, blow_out, drop_height, drop_rate] + [np.nan]*9
        drop_rows.append(drop_row + drop_info)
        i += 1
    return drop_rows

def spin_helper(spin_list, step_num):
    """
    Helper method to retrieve spin info from a worklist
    
    :param spin_list: Data on the spin step in a form such as:
        data['samples']['sample0']['worklist'][1]['details']['steps']
    :param step_num: the step number of the spin action in relation to the previous step 
        in the main function
    
    :return: A list of lists, where each list is a row with step_id and spin variables 
        like acceleration, rpm, etc.
    """
    row_template = [0, 'spin'] + [np.nan]*5
    spin_rows = []
    for spin in spin_list:
        # for each spin step, get the spin-related variables and fill in the step's 
        # information and append to the list of rows
        spin_acc = spin['acceleration']
        spin_duration = spin['duration']
        spin_rpm = spin['rpm']
        spin_row = row_template.copy()
        spin_row = spin_row + [spin_acc, spin_duration, spin_rpm] + [np.nan]*6
        spin_row[0] = step_num
        # account for link steps
        step_num += 2
        spin_rows.append(spin_row)
    return spin_rows

def anneal_helper(anneal_list, step_num):
    """
    Helper method for the anneal/hotplate step
    
    :param anneal_list: the worklist for the anneal step
        e.g. data['samples']['sample0']['worklist'][3]
    :param step_num: the step number of this step in relation to the previous step in the 
        main function
    
    :return: A row consisting of the step_id/number and hotplate variables like temp. 
        and time.
    """
    # get anneal/hotplate information and create step info as a row.
    row_template = [0, 'plate'] + [np.nan]*7
    anneal_list = anneal_list['details']
    anneal_duration = anneal_list['duration']
    anneal_temp = anneal_list['temperature']
    plate = anneal_list['hotplate'].lower()
    anneal_row = row_template.copy()
    anneal_row[0] = step_num
    anneal_row[1] = plate
    anneal_row.append(anneal_duration)
    anneal_row.append(anneal_temp)
    anneal_row = anneal_row + [np.nan]*5
    return [anneal_row]

def rest_helper(rest_list, step_num, tray_num):
    """
    Helper method for the rest step
    
    :param rest_list: the worklist for the rest step, which holds info like how long to rest.
    :param step_num: Step number in relation to previous step
    :param tray_num: the tray number where the sample will rest
    
    :return: returns a list with the step_id, tray info, and rest duration
    """
    row = [0, tray_num.lower()] + [np.nan]*9
    row.append(rest_list['details']['duration'])
    row = row + [np.nan] * 4
    row[0] = step_num
    return [row]

def char_helper(char_list, step_num):
    """
    Characterization helper function. Creates a row for each type of characterization performed on the sample
    
    :param char_list: list of characterization tasks performed on a sample
        data['samples']['sample0']['worklist'][7]['details']['characterization_tasks']
    :param step_num: the step number in relation to the previous step in the main function
    
    returns: list of lists, where each list is a row containing the characterization information for each task
    """
    row_template = [0, 'char'] + [np.nan]*10
    char_rows = []
    # for each characterization task:
    for task in char_list:
        # get the relevant outputs and store them in the row and append each row to the list
        # of rows.
        char_name = task['name']
        detail_keys = list(task['details'].keys())
        char_exposure_time = task['details'][detail_keys[0]]
        char_duration = task['duration']
        char_pos = task['position']
        row = row_template.copy()
        row[0] = step_num
        step_num += 2
        row.append(char_name)
        row.append(char_exposure_time)
        row.append(char_duration)
        row.append(char_pos)
        char_rows.append(row)
    return char_rows

def final_helper(worklist, step_num):
    """
    Helper method for the final action, which is a rest/storage step.
    :param worklist: Contains information about where the sample will rest/be stored.
    
    :return: A row that indicates the final step number and resting location (tray) of the sample
    """
    row_template = [step_num, 'tray#'] + [np.nan]*14
    row_template[1] = worklist['details']['destination'].lower()
    return [row_template]

def action_table(sample, sample_id, batch_id):
    """
    The main function for calling all of the above helper functions to 
    create an action table for each sample within a batch.
    
    :param sample: the sample data, in the format e.g. data['samples']['sample0']
    :param sample_id: A sample identifier used in the data to distinguish between samples in 
        the batch. e.g. a string, 'sample0'
    :param batch_id: A batch identifier used to distinguish between batches. 
        e.g. 'WBG_Repeat_Batch_4_Experiment_1'
    """
    # get sample worklist
    worklist = sample['worklist']
    # step 0 is movement from storage to spincoater, to get ready for drops
    # so we start with worklist step 1
    drop_list = worklist[1]
    
    dissolve_steps = dissolve_helper(drop_list)
    drop_steps = drop_helper(drop_list, dissolve_steps[-1][0])
    # next step is +3 from the previous step_id, to account for a "GOES_INTO" and "NEXT" step
    spin_steps = spin_helper(drop_list['details']['steps'], drop_steps[-1][0]+3)
    # skip 1 step num, to account for link step
    next_step = spin_steps[-1][0] + 2
    anneal_step = anneal_helper(worklist[3], next_step)
    # skip another step for movement from hotplate to tray
    next_step = anneal_step[0][0] + 2
    rest_step = rest_helper(worklist[5], next_step, worklist[4]['details']['destination'])
    # skip another step for movement from rest/storage to characterization
    next_step = rest_step[0][0] + 2
    char_steps = char_helper(worklist[7]['details']['characterization_tasks'], next_step)
    final_step = final_helper(worklist[8], char_steps[-1][0]+2)
    
    actions = dissolve_steps + drop_steps + spin_steps + anneal_step + rest_step + char_steps + final_step
    # add in sample_id and batch_id to each (solar) cell in sample0
    for i in actions:
        i.append(sample_id)
        i.append(batch_id)
    return actions

def save_action_csvs(data):
    batch_id = data['name']
    print(batch_id, sample['name'], data['samples'])
    act_cols =  ['step_id','action','chemical_from','drop_air_gap','drop_blow_out','drop_height','drop_rate','spin_acc','spin_rpm','hp_duration','hp_temp','rest_duration','char_name','char_exposure time','char_duration','char_position','sample_id','batch_id']
    dfs = []
    for sample in data['samples']:
        act = pd.DataFrame(action_table(sample, sample['name'], batch_id))
        df = act.astype({'chemical':'Int64'})
        dfs.append(df)
        fname = batch_id + '_' + sample + '_action.csv'
        df.to_csv(fname,index=False)
        return dfs
        