#  Author: Sofia Minano Gonzalez
#  Date: 14/10/2021
#  Last revision: 14/10/2021
#  Python version: 3.9 (Blender 2.93)
#  Copyright (c) 2021, Sofia Minano Gonzalez
#  All rights reserved.

import csv
import numpy as np
import config

#import pdb


def csv_to_dict_keys_per_row(filename,
                             n_header_rows_to_skip,
                             idx_col_start_data):
    """
    Reads csv with data per rows and returns dictionary with
    - keys = first comma-sep element per row. (For geometry: str with name of geometry centroids (perch edges, plane vertices, obstacles top centres))
    - values = rest of comma-sep elements of the row, starting at col 'idx_col_start_data', and formated as 1-dim numpy array (For geometry: coordinates of centroids)

    Input
    - filename: name of csv file
    - n_header_rows_to_skip: number of rows from the top to skip (typically with metadata)
    - idx_col_start_data: idx of column (numbering starting with 0) from which the rest of the row is taken to make the numpy array for the key = first elem of the row

    """
    with open(filename, mode='r') as infile:
        reader = csv.reader(infile)
        # skip required rows
        for i in range(n_header_rows_to_skip):
            next(reader)
        # make a dict with keys = 1st elem of row, value = numpy array made up of data from idx_col_start_data col
        # til end of row
        dict_geometry = dict()
        for rows in reader:
            if '' in rows[idx_col_start_data:]: #if any is empty: assign all nan
                dict_geometry[rows[0]] = np.array([np.nan]*len(rows[idx_col_start_data:]))
            else:
                dict_geometry[rows[0]] = np.array([np.float(r) for r in rows[idx_col_start_data:]]) # rows is a list where each elem is a comma-sep value

    return dict_geometry


def csv_to_dict_keys_per_col(filename,
                             n_header_rows_to_skip):
    """
    Reads csv with data per column (and typically rows per frame) and returns dictionary with:
    - keys = every element in first csv row, after skipping the required ones
    - values = for every key, a numpy array, made from all the elements in the column corresponding to that key

    Inputs
    - filename: name of csv file
    - n_header_rows_to_skip: number of header rows to skip
    """

    with open(filename, mode='r') as infile:
        reader = csv.reader(infile)
        # skip required rows
        for i in range(n_header_rows_to_skip):
            next(reader)
        # loop thru rows
        for r_i, row_as_list in enumerate(reader):
            # take first row as keys
            if r_i == 0:
                list_of_keys_in_order = row_as_list  # list of keys in order of appearance in csv file!
                dict_transforms = {k: [] for k in list_of_keys_in_order}  # initialise values in dict with empty lists
            # for the rest of rows:
            # append each element in the row to corresponding list of values (following order of appearance)
            # if key contains the string 'frame': format as int; else format as float
            else:
                for i, k in enumerate(list_of_keys_in_order):
                    if 'frame' in k:
                        dict_transforms[k].append(int(row_as_list[i]))
                    else:
                        dict_transforms[k].append(float(row_as_list[i]))
        # transform values into numpy arrays
        for k in list_of_keys_in_order:
            dict_transforms[k] = np.array(dict_transforms[k])

    return dict_transforms

def csv_transforms_concatenated_to_dict(config):
    """
    Creates a dict for the csv transform data per columns, and concatenates the numpy arrays of the required fields
    (typically to concatenate X,Y,Z coords into one key)

    :param config:, contains details of fields to concatenate
    :return:
    """

    # Get dict with keys per column
    dict_transforms = csv_to_dict_keys_per_col(config.transforms_csv_path_to_file,
                                               config.transforms_csv_n_header_rows_to_skip)

    ### concatenate XYZ/WXYZ arrays
    dict_transforms_concatenated = dict()
    # get list of original fields to concatenate
    list_of_fields_to_concatenate = [i
                                     for d in config.dict_fields_after_concat_to_list_of_fields_to_concatenate.values()
                                     for i in d] #it's a dict_values of nested lists, unpack

    # take keys and values from previous dict if not in list of fields to concatenate
    for k in dict_transforms.keys():
        if k not in list_of_fields_to_concatenate:
            dict_transforms_concatenated[k] = dict_transforms[k]

    # for the fields to concatenate:
    for k in config.dict_fields_after_concat_to_list_of_fields_to_concatenate.keys():
        dict_transforms_concatenated[k] = np.concatenate(tuple(dict_transforms[v][:, np.newaxis]
                                                               for v in config.dict_fields_after_concat_to_list_of_fields_to_concatenate[k]),
                                                         axis=1)
    #--------------------------------------------------------------------
    # dict_transforms_concatenated = dict()
    # if config.flag_concatenate_selected_transforms:
    #     # get list of original fields to concatenate
    #     list_of_fields_to_concatenate = [i
    #                                      for d in config.dict_fields_after_concat_to_list_of_fields_to_concatenate.values()
    #                                      for i in d] #it's a dict_values of nested lists, unpack
    #
    #     # take keys and values from previous dict if not in list of fields to concatenate
    #     for k in dict_transforms.keys():
    #         if k not in list_of_fields_to_concatenate:
    #             dict_transforms_concatenated[k] = dict_transforms[k]
    #
    #     # for the fields to concatenate:
    #     for k in config.dict_fields_after_concat_to_list_of_fields_to_concatenate.keys():
    #         dict_transforms_concatenated[k] = np.concatenate(tuple(dict_transforms[v][:, np.newaxis]
    #                                                                for v in config.dict_fields_after_concat_to_list_of_fields_to_concatenate[k]),
    #                                                          axis=1)

    return dict_transforms_concatenated

def csv_to_dict_TO_L_frames(filename,
                             n_header_rows_to_skip,
                             idx_col_start_data):
    """
    Reads csv with data per rows and returns dictionary with
    - keys = first comma-sep element per row.
    - subkeys: taken from the first row after skip
    - values = rest of comma-sep elements of the row, starting at col 'idx_col_start_data', and formatted as list

    Input
    - filename: name of csv file
    - n_header_rows_to_skip: number of rows from the top to skip (typically with metadata)
    - idx_col_start_data: idx of column (numbering starting with 0) from which the rest of the row is taken to make the list for the key = first elem of the row

    """
    with open(filename, mode='r') as infile:
        reader = csv.reader(infile)
        # skip required rows
        for i in range(n_header_rows_to_skip):
            next(reader)
        # make a dict with keys = 1st elem of row, value = list of data from idx_col_start_data col
        # til end of row
        dict_TO_L_frames = dict()
        for i,rows in enumerate(reader):
            if i == 0:
                list_subkeys = rows[idx_col_start_data:]
            else:
                dict_per_trial = dict()
                for k, r in zip(list_subkeys, rows[idx_col_start_data:]):
                    if r == '':
                        dict_per_trial[k] = float('nan')
                    else:
                        dict_per_trial[k] = float(r) #maybe int
                dict_TO_L_frames[rows[0]] = dict_per_trial  # rows is a list where each elem is a comma-sep value

    return dict_TO_L_frames


if __name__ == '__main__':
    config = config.config()

    #### Dict of geometry
    map_geometry = csv_to_dict_keys_per_row(config.geometry_csv_path_to_file,
                                            config.geometry_csv_n_header_rows_to_skip,
                                            config.geometry_csv_idx_col_start_data)

    ### Dict of eyesRF rotation quaternion
    map_eyesRF_quat = csv_to_dict_keys_per_row(config.eyesRF_csv_path_to_file,
                                               config.eyesRF_csv_n_header_rows_to_skip,
                                               config.eyesRF_csv_idx_col_start_data)

    quat_from_headRF_to_eyesRF = map_eyesRF_quat[config.date_bird_HP_pair_str]

    #### Dict of transforms
    map_transforms_concat = csv_transforms_concatenated_to_dict(config)


    ### TO/L frames
    map_TO_L_frames = csv_to_dict_TO_L_frames(config.frames_TO_L_csv_path_to_file,
                                              config.frames_csv_n_header_rows_to_skip,
                                              config.frames_csv_idx_col_start_data)
    #pdb.set_trace()