from json import load, loads
from os import listdir
import pandas as pd
from re import search
import numpy as np

def split_chemicals(input_string):
    result = []
    for i in input_string.split('_'):
        first_digit = search(r'\d+.\d+', i).start()
        result.append((i[:first_digit], float(i[first_digit:])))
    return result

def flatten_chem(sample):
    chem = pd.DataFrame(columns = ['chemical_id', 'batch_id', 'content', 'concentration', 
                                          'molarity', 'volume', 'type'])
    
    chemical_id = 1
    mix_id = 1
    
    sample_id = sample['name']
    worklist = sample['worklist']
    for step in worklist:
        if 'details' in step and 'drops' in step['details']:
            for droplet in step['details']['drops']:
                # if it has both solvent and solute
                if 'solution' in droplet and droplet['solution']['solutes'] != '' and droplet['solution']['solvent'] != '':
                    for solute in split_chemicals(droplet['solution']['solutes']):
                        content, concentration = solute
                        if ((chem['content'] == content) & (chem['concentration'] == concentration)).sum() == 0:
                            new_row = {'chemical_id': chemical_id,
                                       'sample_id': sample_id,
                                       'batch_id': data['name'],
                                       'content': content,
                                       'concentration':concentration, 
                                       'type': 'solute'}
                            chem = chem.append(new_row, ignore_index=True)
                            chemical_id += 1
                    for solvent in split_chemicals(droplet['solution']['solvent']):
                        content, concentration = solvent
                        if ((chem['content'] == content) & (chem['concentration'] == concentration)).sum() == 0:
                            new_row = {'chemical_id': chemical_id, 
                                       'sample_id': sample_id,
                                       'batch_id': data['name'],
                                       'content': content,
                                       'concentration':concentration, 
                                       'type': 'solvent'}
                            chem = chem.append(new_row, ignore_index=True)
                            chemical_id += 1
                    # adding the mix
                    new_row = {'chemical_id': chemical_id,
                               'sample_id': sample_id,
                               'batch_id': data['name'],
                               'volume': droplet['volume'],
                               'content': 'Mix'+str(mix_id),
                               'molarity':droplet['solution']['molarity'], 
                               'type': 'solution'}

                    chem = chem.append(new_row, ignore_index=True)
                    mix_id += 1
                    chemical_id += 1
                # check if the drop is an antisolvent
                if 'solution' in droplet and droplet['solution']['solutes'] == '':
                    # check if the antisolvent is in the df, add to the df if not in the df
                    if (chem['content'] == droplet['solution']['solvent']).sum() == 0:
                        new_row = {'chemical_id': chemical_id, 
                                   'sample_id': sample_id,
                                   'batch_id': data['name'],
                                   'molarity':droplet['solution']['molarity'], 
                                   'content': droplet['solution']['solvent'], 
                                   'type': 'antisolvent'}
                        chem = chem.append(new_row, ignore_index=True)
                        chemical_id += 1
                    # adding the mix
                    new_row = {'chemical_id': chemical_id,
                               'sample_id': sample_id,
                               'batch_id': data['name'],
                               'content': 'Mix'+str(mix_id),
                               'volume': droplet['volume'],
                               'type': 'solution'}

                    chem = chem.append(new_row, ignore_index=True)
                    mix_id += 1
                    chemical_id += 1
    return chem

def save_chem_csvs(data):
    for sample in data['samples']:
        file_name = data['name'] + '_' + sample + '_' + 'chem.csv'
        flatten_chem(data['samples'][sample]).to_csv(file_name, index=False)
    return
    