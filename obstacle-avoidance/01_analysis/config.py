#  Author: Sofia Minano Gonzalez
#  Date: 14/10/2021
#  Last revision: 14/10/2021
#  Python version: 3.9 (Blender 2.93)
#  Copyright (c) 2021, Sofia Minano Gonzalez
#  All rights reserved.

import math
import numpy as np
import os
import load_data
from datetime import datetime
import string
import sys
import json
import pdb
import re

class config():

    def __init__(self,
                 input_json_path):

        ####################################################################
        ### Get kwargs dict from json
        f_inputs_json = open(input_json_path)
        input_json_dict = json.load(f_inputs_json)
        f_inputs_json.close()

        ############################################################
        ### Config params required from input json
        # required means that these keys must be present in input json; if any is not it will throw an error
        # for the rest of input params: if described in input json that overwrites default
        required_input_params_dict = dict()

        # Trial id and render suffix
        required_input_params_dict['trial_str'] = input_json_dict.get('trial_str')
        required_input_params_dict['render_output_suffix'] = input_json_dict.get('render_output_suffix')
        required_input_params_dict['date_bird_HP_pair_str'] = input_json_dict.get('date_bird_HP_pair_str')

        # Paths to CSV with transforms and geometry data
        required_input_params_dict['geometry_csv_date_str'] = input_json_dict.get('geometry_csv_date_str')  
        required_input_params_dict['transforms_csv_date_str'] = input_json_dict.get('transforms_csv_date_str')  
        required_input_params_dict['flag_camera_tracks_trajectoryRF'] = input_json_dict.get('flag_camera_tracks_trajectoryRF') 

        # Paths to CSV with eyesRF and TO-L frames data
        required_input_params_dict['eyesRF_csv_file_str'] = input_json_dict.get('eyesRF_csv_file_str') 
        required_input_params_dict['frames_TO_L_csv_file_str'] = input_json_dict.get('frames_TO_L_csv_file_str') 
        required_input_params_dict['TO_L_csv_folder_path'] = input_json_dict.get('TO_L_csv_folder_path')

        # Flags for camera tracking specific reference frames
        required_input_params_dict['flag_camera_tracks_headRF'] = input_json_dict.get('flag_camera_tracks_headRF')   # default FALSE
        required_input_params_dict['flag_camera_tracks_worldRF'] = input_json_dict.get('flag_camera_tracks_worldRF')  # default FALSE

        # Flag to save config class as json
        required_input_params_dict['flag_save_config_as_json'] = input_json_dict.get('flag_save_config_as_json')  # default: True

        # Check if any of the required input values is None (i.e. the key doesnt exist), and print an error if it happens
        if any(elem is None for elem in required_input_params_dict.values()):
            sys.exit('At least one of the required input parameters for the config class is None. Exiting.... #mebajodelavida')

        # print required input params
        print('--------------------------------------------------------')
        print('Input json file path:')
        print("%s" % input_json_path)
        print(" ")
        print('--------------------------------------------------------')
        print('Parameters specified in input json for this trial:')
        print('--------------------------------------------------------')
        for k in input_json_dict.keys():
            print(k, ':', input_json_dict[k])
        print('------------------------------------')

        # add path to json files with input parameters for config
        self.config_input_json_path = input_json_path

        # add list of required input parameters names to config
        # (required input params are taken from input json and have no 'optional' value)
        self.list_required_input_parameters = list(required_input_params_dict.keys())

        # add list of all parameters defined in input json
        self.list_all_parameters_in_input_json = list(input_json_dict.keys())

        ##########################################################################################
        ###########################################################################################
        ### Paths to input and output dirs
        self.parent_dir_path = input_json_dict.get('parent_dir_path',
                                                   os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # default: two levels up from current file
        self.data_folder_path = input_json_dict.get('data_folder_path',
                                                    os.path.join(self.parent_dir_path, '00_data'))
        self.output_folder_path = input_json_dict.get('output_folder_path',
                                                      os.path.join(self.parent_dir_path, '02_output'))
        # (for eyesRF)
        self.matlab_output_folder_path = input_json_dict.get('matlab_output_folder_path',
                                                             os.path.join(os.path.dirname(self.parent_dir_path), 'Analysis in Matlab', '02_output'))
        # for TO-L frames
        self.TO_L_csv_folder_path = required_input_params_dict['TO_L_csv_folder_path']

        #######################################################################
        ### Trial id and render suffix
        self.date_bird_HP_pair_str = required_input_params_dict['date_bird_HP_pair_str']
        self.trial_str = required_input_params_dict['trial_str']
        # suffix to refer to this rendering (timestamp is added after)
        self.render_output_suffix = required_input_params_dict['render_output_suffix']

        # Check match between trial_str and HP-bird string (I think this is unnecessary....)
        # OJO! for example: self.date_bird_HP_pair_str = 201124_Charmander_HPlmax45
        # regexp: re.sub(r'\d+([bis]+)?$', '', self.trial_str) extracts date_birdname from trial string (see generate_input_json_files_from_template.py)
        if '_'.join(self.date_bird_HP_pair_str.split('_')[0:2]) != re.sub(r'\d+([bis]+)?$', '', self.trial_str): # self.trial_str.rstrip(string.digits): #self.trial_str.rstrip(string.digits) should be *only* date_birdname
            sys.exit("ERROR in config: the headpack-bird pair string does not match the trial string")
        ############################################################################
        ### Dir for render output
        self.timestamp = datetime.today().strftime("%Y%m%d%H%M")
        self.render_output_parent_dir_str = input_json_dict.get('render_output_parent_dir_str',
                                                                '_'.join([self.trial_str,
                                                                         self.render_output_suffix,
                                                                         self.timestamp]))
        self.render_output_parent_dir_path = input_json_dict.get('render_output_parent_dir_path',
                                                                 os.path.join(self.output_folder_path,
                                                                              self.render_output_parent_dir_str, ''))  # adding '' to os.path.join I add a trailing slash, indep of OS

        #########################################################################################
        ### Paths to CSV data files

        ## Geometry: date strings in geometry csv data to use (from data folder in self.data_folder_path)
        self.geometry_csv_date_str = required_input_params_dict['geometry_csv_date_str']

        ## Transforms: date strings in transforms csv data to use
        self.transforms_csv_date_str = required_input_params_dict['transforms_csv_date_str']
        # select whether rotations in transform track trajectoryRF
        self.flag_camera_tracks_trajectoryRF = required_input_params_dict['flag_camera_tracks_trajectoryRF']

        ## EyesRF data (not in self.data_folder_path, in output from 'Analysis in Matlab'!)
        self.eyesRF_csv_file_str = required_input_params_dict['eyesRF_csv_file_str']
        self.eyesRF_csv_path_to_file = input_json_dict.get('eyesRF_csv_path_to_file',
                                                           os.path.join(self.matlab_output_folder_path,
                                                                        self.eyesRF_csv_file_str))

        ## TO/L frames data (not in self.data_folder_path)
        self.frames_TO_L_csv_file_str = required_input_params_dict['frames_TO_L_csv_file_str']
        self.frames_TO_L_csv_path_to_file = input_json_dict.get('frames_TO_L_csv_path_to_file',
                                                                os.path.join(self.TO_L_csv_folder_path,
                                                                             self.frames_TO_L_csv_file_str))

        ####################################################################################################3
        ### Save config as json file
        # saves a json file for this rendering with the config params, in the render output folder
        self.flag_save_config_as_json = required_input_params_dict['flag_save_config_as_json']
        self.keys_to_exclude_from_config_dict = input_json_dict.get('keys_to_exclude_from_config_dict',
                                                                    ['frames_TO_L_frames_from_video_review_dict',
                                                                     'eyesRF_quat_dict']) # bc numpy arrays are not serializable...

        ##########################################################################################################################3
        ### Parameters for reading/loading csv data
        ## Geometry csv to dict
        self.geometry_csv_file_str = input_json_dict.get('geometry_csv_file_str',
                                                         self.trial_str + '_geometry_export_' + self.geometry_csv_date_str + '.csv')
        self.geometry_csv_path_to_file = input_json_dict.get('geometry_csv_path_to_file',
                                                             os.path.join(self.data_folder_path,
                                                                          'Geometry',
                                                                          self.geometry_csv_date_str,
                                                                          self.date_bird_HP_pair_str,
                                                                          self.geometry_csv_file_str))
        self.geometry_csv_n_header_rows_to_skip = input_json_dict.get('geometry_csv_n_header_rows_to_skip',
                                                                      1)
        self.geometry_csv_idx_col_start_data = input_json_dict.get('geometry_csv_idx_col_start_data',
                                                                   1)  # number of col (starting with 0) where numpy array assigned to the key=first csv elem starts

        ## Transforms csv to dict------------------------------------------------------------------------------------------------------------
        # load transform data
        if not self.flag_camera_tracks_trajectoryRF:
            self.transforms_csv_file_str = input_json_dict.get('transforms_csv_file_str',
                                                               self.trial_str + '_transforms_export_' + self.transforms_csv_date_str + '.csv')
            self.transforms_csv_path_to_file = input_json_dict.get('transforms_csv_path_to_file',
                                                                   os.path.join(self.data_folder_path, 'Transforms',
                                                                                self.transforms_csv_date_str,
                                                                                self.date_bird_HP_pair_str,
                                                                                self.transforms_csv_file_str))
        # or transform data for trajectoryRF if required
        else:
            self.transforms_csv_file_str = input_json_dict.get('transforms_csv_file_str',
                                                      self.trial_str + '_transforms_trajectoryRF_export_' + self.transforms_csv_date_str + '.csv')
            self.transforms_csv_path_to_file = input_json_dict.get('transforms_csv_path_to_file',
                                                                   os.path.join(self.data_folder_path, 'Transforms_trajectoryRF',
                                                                                self.transforms_csv_date_str,
                                                                                self.date_bird_HP_pair_str,
                                                                                self.transforms_csv_file_str))
        self.transforms_csv_n_header_rows_to_skip = input_json_dict.get('transforms_csv_n_header_rows_to_skip',
                                                                        1)

        # concatenate selected columns of transform CSV
        # (I don't think a user would need to change these... so no kwargs.get for now)
        if not self.flag_camera_tracks_trajectoryRF:
            self.list_fields_after_concatenating = ['transform_t_XYZ',
                                                    'transform_t_interp_XYZ',
                                                    'transform_q_WXYZ',
                                                    'transform_q_interp_WXYZ']
        else:
            self.list_fields_after_concatenating = ['transform_t_interp_XYZ', 'transform_q_interp_WXYZ']  # for trajectoryRF: only interp fields!
        self.dict_fields_after_concat_to_list_of_fields_to_concatenate = \
            {k_str: [k_str[0:[i for i, s in enumerate(k_str) if s == '_'][-1] + 1] + x for x in
                     list(k_str.split('_')[-1])]
             for k_str in self.list_fields_after_concatenating}

        ## Rotation from headRF to eyesRF csv to dict (keys: bird-HP pairs)
        self.eyesRF_csv_n_header_rows_to_skip = input_json_dict.get('eyesRF_csv_n_header_rows_to_skip',
                                                                    4)
        self.eyesRF_csv_idx_col_start_data = input_json_dict.get('eyesRF_csv_idx_col_start_data',
                                                                 2)  # number of col (starting with 0) where numpy array assigned to the key=first csv elem starts

        ## Frames TO and L from video review csv to dict (keys: trials)
        self.frames_csv_n_header_rows_to_skip = input_json_dict.get('frames_csv_n_header_rows_to_skip',
                                                                    5)
        self.frames_csv_idx_col_start_data = input_json_dict.get('frames_csv_idx_col_start_data',
                                                                 8)

        ##############################################################################################################
        ### Add selected data directly to config: frames TO-L and eyesRF rot quat
        ## Add frames TO-L dict to config
        self.frames_TO_L_frames_from_video_review_dict = load_data.csv_to_dict_TO_L_frames(self.frames_TO_L_csv_path_to_file,
                                                                                           self.frames_csv_n_header_rows_to_skip,
                                                                                           self.frames_csv_idx_col_start_data)

        ## Add eyesRF quaternions (to rotate from headRF ref pose to eyesRF) to config
        self.eyesRF_quat_dict = load_data.csv_to_dict_keys_per_row(self.eyesRF_csv_path_to_file,
                                                                   self.eyesRF_csv_n_header_rows_to_skip,
                                                                   self.eyesRF_csv_idx_col_start_data)

        ######################################################################################################################
        ### Scene parameters
        self.units_system = input_json_dict.get('units_system',
                                                'METRIC')
        self.units_rotation = input_json_dict.get('units_rotation',
                                                  'DEGREES')  # OJO (quaternions always in rad anyways)
        self.mm_to_m = 1 / 1000  # this is not a configurable param...
        # self.mm_to_m = input_json_dict.get('mm_to_m',
        #                                     1 / 1000)

        ######################################################################################################################
        ### Additional geometry parameters
        ## Perches
        # estimates from reference video snapshots; see 'D:\EXPTS NOV 2018\Visual field reconstruction Nov 2020\Geometry and pose reconstruction in Blender\00_data\estimating perch geometry as cylinder'
        self.perch_radius = input_json_dict.get('perch_radius',
                                                40)  # mm
        self.perch_marker_centre_to_cyl_axis_z_offset = input_json_dict.get('perch_marker_centre_to_cyl_axis_z_offset',
                                                                            40)  # mm

        ## Obstacles
        # estimate from mean deviation of top marker z-coord from 2m; see 'D:\EXPTS NOV 2018\Validation experiments Nov 2020\01_analysis\bird_flights\estimate_large_markers_z_offset_and_perches_dimensions.m'
        self.obs_radius = input_json_dict.get('obs_radius',
                                              150)  # mm, diameter=300mm
        self.marker_centre_to_top_obs_base = input_json_dict.get('marker_centre_to_top_obs_base',
                                                                 14)  # mm;

        ## Planes (ceiling, walls, floor)
        self.n_vertices_per_plane = input_json_dict.get('n_vertices_per_plane',
                                                        4)

        ## Lamps
        self.list_tuples_location_lamps_in_mm = input_json_dict.get('list_tuples_location_lamps_in_mm',
                                                                    [(0.0, 2000.0, 3000.0),
                                                                     (0.0, -3500.0, 3000.0),
                                                                     (0.0, -9000.0, 3000.0)])  # mm
        self.list_tuples_rotation_euler_lamps_in_rad = input_json_dict.get('list_tuples_rotation_euler_lamps_in_rad',
                                                                           [(0.0, -math.pi, 0.0),
                                                                            (0.0, -math.pi, 0.0),
                                                                            (0.0, -math.pi, 0.0)])  # rad!
        self.n_lamps = len(self.list_tuples_location_lamps_in_mm)
        self.list_lamps_strength = input_json_dict.get('list_lamps_strength',
                                                        [1, 2, 1])

        #####################################################################################################
        ### Materials
        self.dict_geometry_to_material_hex_str_and_alpha = input_json_dict.get('dict_geometry_to_material_hex_str_and_alpha',
                                                                              {'floor': ['629E1D', 1],
                                                                               'wall_xmax': ['B49857', 1],
                                                                               'wall_xmin': ['B49857', 1],
                                                                               'wall_ymax': ['B49857', 1],
                                                                               'wall_ymin': ['B49857', 1],
                                                                               'high_obs_1': ['CFCFCF', 1],
                                                                               'high_obs_2': ['CFCFCF', 1],
                                                                               'high_obs_3': ['CFCFCF', 1],
                                                                               'high_obs_4': ['CFCFCF', 1],
                                                                               'ceiling': ['D5D5D5', 1],
                                                                               'ini_perch': ['A8493C', 1],
                                                                               'end_perch': ['3535E7', 1]})

        ################################################################################################################
        ### Camera parameters
        ## Initial state
        # location
        self.ini_camera_location = input_json_dict.get('ini_camera_location',
                                                       (0.0, 0.0, 0.0))  # m
        # rotation (as quaternion!)
        self.ini_camera_rotation_quat = input_json_dict.get('ini_camera_rotation_quat',
                                                            (1.0, 0.0, 0.0, 0.0))  # quaternion: (w,x,y,z) (default: (1.0, 0.0, 0.0, 0.0))

        ## Camera parameters
        self.camera_type = input_json_dict.get('camera_type',
                                               'PANO')
        self.camera_panorama_type = input_json_dict.get('camera_panorama_type',
                                                        'EQUIRECTANGULAR')  # 'FISHEYE_EQUIDISTANT' 'EQUIRECTANGULAR'

        self.camera_longitude_min_max_in_rad = input_json_dict.get('camera_longitude_min_max_in_rad',
                                                                   [-math.pi,
                                                                    math.pi])  # in rad!!
        self.camera_latitude_min_max_in_rad = input_json_dict.get('camera_latitude_min_max_in_rad',
                                                                  [-0.5 * math.pi,
                                                                   0.5 * math.pi])  # in rad!!
        self.camera_shift_x_y = input_json_dict.get('camera_shift_x_y',
                                                    [0, 0])
        self.camera_clip_start_end_in_m = input_json_dict.get('camera_clip_start_end_in_m',
                                                              [1e-6, 100])  # m
        self.camera_sensor_width = input_json_dict.get('camera_sensor_width',
                                                       32)  # default value, Im not sure if relevant
        self.sensor_fit = input_json_dict.get('sensor_fit',
                                              'AUTO')  # adjust depending on resolution
        self.camera_fisheye_equidistant_FOV_in_rad = input_json_dict.get('camera_fisheye_equidistant_FOV_in_rad',
                                                                         277 * math.pi / 180)  # rad #only applicable if self.camera_panorama_type = FISHEYE_EQUIDISTANT

        #################################################################################################################
        ### Rendering parameters
        ## Device
        self.render_device = input_json_dict.get('render_device',
                                                 'GPU')  # engine: always Cycles

        ## Pixel filtering
        # Z, Material and Object passes are not anti-aliased; but Vector is. I disable it using the Box filter
        # with Box: pixel samples stay withi pixel (https://blender.stackexchange.com/questions/129636/how-does-anti-aliasing-work-in-cycles)
        self.pixel_filter_type = input_json_dict.get('pixel_filter_type',
                                                     'BOX')  # preferred: BOX; options: BOX=no pixel filtering, BLACKMAN_HARRIS = Blackman Harris filter (this is the default in Blender, with pixel width 1.5)

        #################################################################################################################
        ## Image pixel resolution
        # compute pixel resolution, considering max/min long and lat are the edges of the rendered image

        # Pixels per deg is the input design parameter (how many pixels per degree in latitude and long direction? --same for both directions)
        self.pixels_per_deg = input_json_dict.get('pixels_per_deg',
                                                  5)

        # Longitude and latitude range (in deg) covered in the image
        self.longitude_range_in_deg = np.rad2deg(abs(np.diff(self.camera_longitude_min_max_in_rad))).item()
        self.latitude_range_in_deg = np.rad2deg(abs(np.diff(self.camera_latitude_min_max_in_rad))).item()

        # Number of pixels in x and y direction (columns and rows respectively)
        # OJO! Blender will round to the nearest integer the pixel number, if it's a real
        self.render_resolution_x_y_in_pixels = input_json_dict.get('render_resolution_x_y_in_pixels',
                                                                   [self.longitude_range_in_deg*self.pixels_per_deg,
                                                                    self.latitude_range_in_deg*self.pixels_per_deg])

        # Check if the number of pixels in x,y direction is all integers
        # if not, round up, and adjust min and max lat-long so that the pixel per deg value stays the same!
        # (if I don't round up, Blender rounds to the nearest integer and the requested pixel per deg value won't be the true value anymore)
        if not all(x.is_integer() for x in self.render_resolution_x_y_in_pixels):  # OJO! is integer, not *of type* int!
            # print warning
            print('--------------------------------------------------------------------------------------------------')
            print('WARNING: the number of pixels in x and/or y direction is a non-integer value ({}), '
                  'for the requested pixels per degree ({}), longitude range ({} deg) and latitude range ({} deg). '
                  'It will be rounded up to {}, and the lat and long mins and maxs will adjusted (keeping the same pixels_per_deg value '
                  'and the same minimum longitude and latitude values)'
                  .format(self.render_resolution_x_y_in_pixels,
                          self.pixels_per_deg,
                          self.longitude_range_in_deg,
                          self.latitude_range_in_deg,
                          [int(math.ceil(elem)) for elem in self.render_resolution_x_y_in_pixels]))

            # set the number of pixels in x and y direction to the round up value
            self.render_resolution_x_y_in_pixels = [int(math.ceil(elem))
                                                    for elem in self.render_resolution_x_y_in_pixels]

            # re-compute the longitude and latitude range in deg
            self.longitude_range_in_deg = self.render_resolution_x_y_in_pixels[0]/self.pixels_per_deg
            self.latitude_range_in_deg = self.render_resolution_x_y_in_pixels[1]/self.pixels_per_deg

            # re-compute the min/max long and latitude (in rad!!), keeping min constant
            # (keeping min constant is just a choice, it could be keeping max constant, but I need to adjust them to keep the pixel per deg value requested)
            self.camera_longitude_min_max_in_rad = [self.camera_longitude_min_max_in_rad[0],
                                                    self.camera_longitude_min_max_in_rad[0] + np.deg2rad(self.longitude_range_in_deg).item()]
            self.camera_latitude_min_max_in_rad = [self.camera_latitude_min_max_in_rad[0],
                                                   self.camera_latitude_min_max_in_rad[0] + np.deg2rad(self.latitude_range_in_deg).item()]

            # print new long/lat min and max
            print('New camera longitude min-max in rad: {}'.format(self.camera_longitude_min_max_in_rad))
            print('New camera longitude min-max in rad: {}'.format(self.camera_latitude_min_max_in_rad))
            print('--------------------------------------------------------------------------------------------------')


        ################################################################################################################
        # Pixel resolution percentage
        self.render_resolution_percentage = input_json_dict.get('render_resolution_percentage',
                                                                100)
        # Pixel aspect ratio
        self.render_pixel_aspect_x_y = input_json_dict.get('render_pixel_aspect_x_y',
                                                           [1, 1])

        ################################################################################################################
        ## Start/end frames for animation (and rendering if --render-anim flag is used)
        # Get TO-L frames for first and second leg
        # leg 1
        frame_TO_1 = self.frames_TO_L_frames_from_video_review_dict[self.trial_str]['frame_TO_1']
        frame_L_1 = self.frames_TO_L_frames_from_video_review_dict[self.trial_str]['frame_L_1']
        # leg 2
        frame_TO_2 = self.frames_TO_L_frames_from_video_review_dict[self.trial_str]['frame_TO_2']
        frame_L_2 = self.frames_TO_L_frames_from_video_review_dict[self.trial_str]['frame_L_2']

        ## Get from input json the suggested frame range for rendering from command line, if it exists
        # (this is simply added to the config for documentation, but it's not used in this script!)
        # (this script doesnt do rendering, it simply creates the scene and defines the animation from TO_1 to L_2)
        self.suggested_frame_range_for_cli_rendering_leg_1 = \
            input_json_dict.get('suggested_frame_range_for_cli_rendering_leg_1',[])
        self.suggested_frame_range_for_cli_rendering_leg_2 = \
            input_json_dict.get('suggested_frame_range_for_cli_rendering_leg_2', [])

        # check if the suggested frame range matches TO-L frames per leg (if they don't, it's not necessarily a problem!)
        if not self.suggested_frame_range_for_cli_rendering_leg_1:
            print('-------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print('WARNING: No suggested frame range for command line rendering defined for leg 1 of this trial, in input json file ')
        elif self.suggested_frame_range_for_cli_rendering_leg_1 != [frame_TO_1, frame_L_1]:
            print('-------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print('WARNING: The first part of the suggested frame range to render ({}) '
                  'does not match the TO and L frames of leg 1 of the trial ({})'.format(self.suggested_frame_range_for_cli_rendering_leg_1,
                                                                                    [frame_TO_1, frame_L_1]))

        if not self.suggested_frame_range_for_cli_rendering_leg_2:
            print('-------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print('WARNING: No suggested frame range for command line rendering defined for leg 2 of this trial, in input json file ')
        elif self.suggested_frame_range_for_cli_rendering_leg_2 != [frame_TO_2, frame_L_2]:
            print('-------------------------------------------------------------------------------------------------------------------------------------------------------------------')
            print('WARNING: The second part of the suggested frame range to render ({}) '
                  'does not match the TO and L frames of leg 2 of the trial ({})'.format(self.suggested_frame_range_for_cli_rendering_leg_2,
                                                                                     [frame_TO_2, frame_L_2]))
        print('-------------------------------------------------------------------------------------------------------------------------------------------------------------------')

        ## Define start/end frames for animation ('rendering' if using --render-anim)!!!
        # OJO!!! These are not the actually rendered frames if a different range of frames is specified via Blender command line arguments!!!
        # I still call it render
        #  - that is, if I run blender from the terminal with --render-anim, then these frames will be the start and end of the rendering
        #  - but if I run blender from the terminal with --render-frame, I can specify a different (non consecutive) range of frames (within the animation range of frames), and that will have priority over the animation ones
        #  - via GUI/scripting I cannot define non-consecutive range of frames (unless I change the whole rendering approach, and I render each frame via scripting)
        #  - so for now with this script I define the keyframes for the complete animation from TO-1 to L-2, and if I want to render a subset of those only then I specify that via scripting
        self.animation_frame_start_end = input_json_dict.get('animation_frame_start_end',
                                                          [int(frame_TO_1),
                                                           int(frame_L_2)])  # matches Vicon frames

        ## Frame rate and frame step
        self.render_frame_step = input_json_dict.get('render_frame_step',
                                                     1)
        self.render_fps = input_json_dict.get('render_fps',
                                              30)  # (I think this is only atually used by Blender if I render a video)

        ## Passes
        self.render_use_pass_combined = input_json_dict.get('render_use_pass_combined', True)  # default: True; even if set to False it will produce it; combined=RGBA
        self.render_use_pass_z = input_json_dict.get('render_use_pass_z', True)
        self.render_use_pass_object_index = input_json_dict.get('render_use_pass_object_index', True)
        self.render_use_pass_vector = input_json_dict.get('render_use_pass_vector', True)

        ## Metadata stamps
        self.render_use_stamp = input_json_dict.get('render_use_stamp', True)
        self.render_use_stamp_time = input_json_dict.get('render_use_stamp_time', False)
        self.render_use_stamp_date = input_json_dict.get('render_use_stamp_date', False)
        self.render_use_stamp_render_time = input_json_dict.get('render_use_stamp_render_time', True)   # -----------
        self.render_use_stamp_frame = input_json_dict.get('render_use_stamp_frame', True)
        self.render_use_stamp_scene = input_json_dict.get('render_use_stamp_scene', False)
        self.render_use_stamp_filename = input_json_dict.get('render_use_stamp_filename', False)
        self.render_use_stamp_camera = input_json_dict.get('render_use_stamp_camera', False)

        ## Output format
        self.render_use_overwrite = input_json_dict.get('render_use_overwrite', True)
        self.render_use_file_extension = input_json_dict.get('render_use_file_extension', True)
        self.render_use_render_cache = input_json_dict.get('render_use_render_cache', False)
        self.render_output_file_format = input_json_dict.get('render_output_file_format', 'OPEN_EXR_MULTILAYER')  # Options: 'OPEN_EXR_MULTILAYER' or 'PNG'. For PNG I use default compression 15%
        self.render_image_color_mode = input_json_dict.get('render_image_color_mode', 'RGBA')
        self.render_image_color_depth = input_json_dict.get('render_image_color_depth', '32')  # Options: 16 or 32 for 'OPEN_EXR_MULTILAYER'; 8 por 16 for 'PNG'
        self.render_image_exr_codec = input_json_dict.get('render_image_exr_codec', 'ZIP')  # default
        self.render_image_use_preview = input_json_dict.get('render_image_use_preview', False)   # if true, saves as JPEG as well

        ###########################################################################################################################
        ### Camera keyframes definition
        ## Interpolation between keyframes
        self.interpolation_between_keyframes = input_json_dict.get('interpolation_between_keyframes',
                                                                   'CONSTANT') # CONSTANT= value between frames is equal to the previous frame value (no interpolation) Other: LINEAR (it shuldn't really matter but just to be sure)

        ## Camera orientation wrt worldRF
        # OJO! In Blender Euler angles are rotations with respect to GLOBAL AXES. So if it is 'XYZ': first rotation is
        # around Xglobal, and second is around Yglobal (!!!), not the new Y-axis!, and third around Zglobal (not the new Zaxis!!)
        self.eul_worldRF_to_cameraRF_rad = input_json_dict.get('eul_worldRF_to_cameraRF_rad',
                                                               ((-.5 * math.pi, math.pi, 0.0),  # in rad!
                                                                'XYZ'))

        ## Use interpolated (or not interp) transform data to define keyframes
        # Select whether to use interpolated transforms from csv, or 'raw' transforms
        self.flag_use_transform_interp = input_json_dict.get('flag_use_transform_interp',
                                                             True)  # recommended: true

        ##########################################################################################
        ## Special cases for the reference frame camera will track
        # in order they are checked in if case....
        # if the following are all false: then the camera tracks eyesRF

        ## Opt 1: camera tracks trajectoryRF
        # to produce a rendering in which the camera follows trajectoryRF
        # flag_camera_tracks_trajectoryRF --above! when loading csv!

        ## Opt 2: camera tracks headRF (coordinate system linked to headpack)
        self.flag_camera_tracks_headRF = input_json_dict.get('flag_camera_tracks_headRF',
                                                             required_input_params_dict['flag_camera_tracks_headRF'])  # default FALSE

        ## Opt 3: camera always parallel to worldRF
        # to produce a rendering in which camera is always parallel to world axes
        self.flag_camera_tracks_worldRF = input_json_dict.get('flag_camera_tracks_worldRF',
                                                              required_input_params_dict['flag_camera_tracks_worldRF'])  # default FALSE

        ## Opt 4: camera tracks eyesRF (coordinate system linked to visual system)
        # if all the rest are false (default), then the camera tracks eyesRF

        # Check flags are consistent:
        # if not all are False, or if not only one is True: print error and exit
        if sum([self.flag_camera_tracks_trajectoryRF,
                self.flag_camera_tracks_headRF,
                self.flag_camera_tracks_worldRF]) > 1:
            sys.exit('Special cases for the reference frame the camera is tracking are not consistent')

        ######################################################################################
        ### Object indices
        # perches IDs
        self.dict_perch_str_to_object_index = input_json_dict.get('dict_perch_str_to_object_index',
                                                                  {'ini_perch': 5,
                                                                   'end_perch': 6})

        # obstacles IDs (I use obstacle ID instead of obstacle str for consistency with Matlab code...possibly change?)
        self.flag_use_obstacle_ID_as_object_index = input_json_dict.get('flag_use_obstacle_ID_as_object_index',
                                                                        True)
        # if 'flag_use_obstacle_ID_as_object_index' = False, then use the following map
        self.dict_obs_ID_to_object_index = input_json_dict.get('dict_obs_ID_to_object_index',
                                                               {'high_obs_1': 1,
                                                                'high_obs_2': 2,
                                                                'high_obs_3': 3,
                                                                'high_obs_4': 4})

        # planes: walls, floor, ceiling
        # walls clockwise from back wall at TO (wall_ymax), then floor and ceiling?
        self.dict_planes_str_to_object_index = input_json_dict.get('dict_planes_str_to_object_index',
                                                                   {'wall_ymax': 7,
                                                                    'wall_xmax': 8,
                                                                    'wall_ymin': 9,
                                                                    'wall_xmin': 10,
                                                                    'floor': 11,
                                                                    'ceiling': 12})
        # check indices for object ID are unique
        self.list_indices_for_object_ID = list(self.dict_perch_str_to_object_index.values()) \
                                           + list(self.dict_obs_ID_to_object_index.values())   \
                                           + list(self.dict_planes_str_to_object_index.values())
        if len(set(self.list_indices_for_object_ID)) != len(self.list_indices_for_object_ID):
            sys.exit("ERROR in config: the indices for Blender's object ID are not unique")
