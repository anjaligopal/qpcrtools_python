#!/usr/bin/python

import numpy as np
import pandas as pd
import os 
import csv
import math

def import_plate(file, save_tabular = True):
    '''
    Imports a plate either from a csv, xls, or xlsx
    file and converts into a tabular plate format.

    Input: plate file, either csv or excel file. 
           See sample for more information.

    Output: plate layout in tabular format (pandas)
    '''

    # Checking the file extension
    file_extension = os.path.splitext(file)[-1];
    
    # Reading file depending on whether it's excel or csv
    if file_extension == ".xls" or file_extension == ".xlsx":
        plate_file = pd.read_excel(file, index_col=1)
    else:
        plate_file = pd.read_csv(file)


    # Creating a list of plate indices
    plate_rows = ['A','B','C','D','E','F','G','H']
    plate_columns = np.arange(12) + 1

    plate_indices = [];
    for row in plate_rows:
        plate_indices.extend([row + str(column) for column in plate_columns])


    # Reading and re-shpaing plate file
    plate = np.array(pd.read_excel(file,na_filter=False))
    plate = plate.reshape(-1,1).flatten();


    # Splitting plate entries by \n
    # We have to check for entries that are null
    plate_entry_values = [];

    for entry in plate:
        entry_split = entry.split("\n");
        if len(entry_split) == 1:
            entry_split = [entry, '']

        plate_entry_values.extend([entry_split])

    # Reshaping and concatenating arrays
    plate_indices = np.array(plate_indices).reshape(96,1)
    plate_entry_values = np.array(plate_entry_values).reshape(96,2)
    plate_tabular = np.concatenate((plate_indices,plate_entry_values),axis=1)

    # Converting to pandas file
    plate_tabular = pd.DataFrame(plate_tabular,columns=['Well','Sample','Replicate'])

    if save_tabular == True:
    	plate_tabular.to_csv(os.path.splitext(file)[0]+'.csv',header=True,index=False);

    return(plate_tabular)

def create_plate(plate_layout, output_file="example_data/plate_layout.txt", 
    reporter = 'FAM', quencher = 'NFQ-MGB', task = 'UNKNOWN', 
    sample_color = '"RGB(0,139,69)"', target_color = '"RGB(0,139,69)"', 
    header_file = 'example_data/plate_header.txt'):

    '''
    Takes a tabular plate layout (pandas data frame) format as input 
    and outputs a qPCR plate layout file.
    '''

    sample_columns = ['Well','Well Position','Sample Name','Sample Color','Biogroup Name','Biogroup Color','Target Name','Target Color','Task','Reporter','Quencher','Quantity','Comments']
    plate_setup = pd.DataFrame(np.empty((96,len(sample_columns)))*np.nan,columns=sample_columns)


    plate_setup['Well'] = np.arange(96)+1
    plate_setup['Well Position'] = plate_layout['Well']
    plate_setup['Sample Name'] = plate_layout['Sample']
    plate_setup['Target Name'] = plate_layout['Replicate']


    quencher_array = []
    reporter_array = []
    task_array = [];
    sample_color_array = [];
    target_color_array = [];

    reporter = 'FAM'
    quencher = 'NFQ-MGB'
    task = 'UNKNOWN'
    sample_color = '"RGB(0,139,69)"'
    target_color = '"RGB(0,139,69)"';

    for i, sample in enumerate(plate_setup['Sample Name']):
        if sample == '':
            quencher_array.append('')
            reporter_array.append('')
            task_array.append('')
            sample_color_array.append('')
            target_color_array.append('')
            
        else:
            quencher_array.append(quencher)
            reporter_array.append(reporter)
            task_array.append(task)
            sample_color_array.append(sample_color)
            target_color_array.append(target_color)

    plate_setup['Sample Color'] = sample_color_array; 
    plate_setup['Target Color'] = target_color_array; 
    plate_setup['Task'] = task_array;
    plate_setup['Reporter'] = reporter_array;
    plate_setup['Quencher'] = quencher_array;

    plate_setup.to_csv(output_file,sep="\t",header=True,index=False, quoting=csv.QUOTE_NONE)

    ### Merging files

    # Header File
    with open(header_file) as file:
        header_text = file.read()

    # Plate files
    with open(output_file) as file:
        plate_file = file.read();

    # Merge two files for adding the data of trial.py from next line
    merged_file = header_text +'\n'+ plate_file;

    with open(output_file, 'w') as file:
        file.write(merged_file)