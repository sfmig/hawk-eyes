"""
This script reconstructs the simplified geometry of the selected experiment, and defines the passes to render
 from a virtual camera that tracks the specified translation and rotation

The process is as follows:
- instantiate config,
- load camera transform data and geometry data,
- build the geometry of the scene,
- create a virtual camera with the required rendering parameters,
- inserts the camera keyframes
- save the input config as a json file

This script is based on an earlier version (main.py) for Blender 2.79.
This version should works for 2.81 (API breaking release)

------------------------------------------------------------------------
To run from the terminal but showing Blender GUI
------------------------------------------------------------------------
Run from the terminal but also start the GUI (it won't start rendering)
    blender
    --python "D:\EXPTS NOV 2018\Visual field reconstruction Nov 2020\Geometry and pose reconstruction in Blender\01_analysis\main.py"
    --
   "D:\EXPTS NOV 2018\Visual field reconstruction Nov 2020\Geometry and pose reconstruction in Blender\00_data\config_input_files\config_input_files_TEST_laptop_202110152117\201124_Drogon16_TEST_laptop_202110152117.json"
------------------------------------------------------------------------
To run on command line and start rendering:
( see example at https://developer.blender.org/diffusion/B/browse/master/release/scripts/templates_py/background_job.py)
------------------------------------------------------------------------
Example to run Blender 2.93 from terminal with arguments for python
    "C:\Program Files\Blender Foundation\Blender 2.93\blender.exe" --background
    --python "D:\EXPTS NOV 2018\Visual field reconstruction Nov 2020\Geometry and pose reconstruction in Blender\01_analysis\main.py"
    --render-anim
    --
    "D://EXPTS NOV 2018//Visual field reconstruction Nov 2020//Geometry and pose reconstruction in Blender//00_data//config class input params//201124_Drogon16_config_class_inputs.json"

If Blender is on system path (OJO with version)
    blender --background
    --python "D:\EXPTS NOV 2018\Visual field reconstruction Nov 2020\Geometry and pose reconstruction in Blender\01_analysis\main.py"
    --render-anim
    --
    "D://EXPTS NOV 2018//Visual field reconstruction Nov 2020//Geometry and pose reconstruction in Blender//00_data//config class input params//201124_Drogon16_config_class_inputs.json"

NOTES:
    - OJO with Blender version! I updated Blender to 2.93 ('blender' in the system path in my laptop now points to 2.93)
    - Python inputs
            --config_class_inputs_json (positional and required)
            --modules_path="D://EXPTS NOV 2018//Visual field reconstruction Nov 2020//Geometry and pose reconstruction in Blender//01_analysis" (optional)
    - if modules_path is not specified, the default value is used (the parent dir to this python script)


------------------------------------------------------------------------
Notes/Useful resources
------------------------------------------------------------------------
* Command line arguments
    * Render frames: --render-anim or -a will render frames from start to end
    * It is also possible to render a discont sequence of frames! (see https://docs.blender.org/manual/en/2.81/advanced/command_line/arguments.html)
    * Blender flags in CLI: '--' causes blender to ignore all following arguments so python can use them.
    * To stop execution from the command line: Ctrl+break (in Dell, Ctrl+Fn+B)
    * Command line arguments for Blender: https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html

* To inspect variables:
    https://docs.blender.org/api/2.81/info_tips_and_tricks.html#drop-into-a-python-interpreter-in-your-script
    OPTION 1: use 'code' module (works in Python interactive terminal in Blender and in Windows terminal)
            import code
            code.interact(local=locals()) # place at the point you'd like to inspect
        pdb works if run from terminal but not with Python console in Blender

    OPTION 2: use IPython
        import IPython
        IPython.embed()

    OPTION 3: use pdb (a bit buggy tho, sometimes Blender crashes)
    run from Blender gui after opening Python terminal from Blender

* To get path to Python executable:
    bpy.app.binary_path_pythonbp

* Useful resources
    http://web.purplefrog.com/~thoth/blender/python-cookbook/
    https://docs.blender.org/api/current/info_tips_and_tricks.html
    https://docs.blender.org/manual/en/2.81/advanced/command_line/arguments.html

-----------------------------------------
Author: Sofia Minano Gonzalez
Date: 14/10/2021
Last revision: 14/10/2021
Python version: 3.9 (Blender 2.93)
Copyright (c) 2021, Sofia Minano Gonzalez
All rights reserved.

"""


def main():

    #####################
    # Instantiate config
    ######################
    # get params for config class from input json file
    input_config = config.config(args.config_class_inputs_json)

    #####################################
    # Load geometry and transforms data
    #####################################
    # geometry
    geometry_dict = load_data.csv_to_dict_keys_per_row(input_config.geometry_csv_path_to_file,
                                                       input_config.geometry_csv_n_header_rows_to_skip,
                                                       input_config.geometry_csv_idx_col_start_data)
    # transforms
    transforms_dict = load_data.csv_transforms_concatenated_to_dict(input_config)

    ##################
    # Prepare scene
    #################
    # Get scene variable
    scene = bpy.context.scene

    # Set scene units
    scene.unit_settings.system = input_config.units_system
    scene.unit_settings.system_rotation = input_config.units_rotation

    ##############################
    # Build geometry in the scene
    ##############################
    define_geometry.create_environment(geometry_dict,
                                       input_config)


    ###############################################################
    # Add virtual camera with required camera and rendering params
    ###############################################################
    # Create camera
    camera_object = define_camera.create_camera(scene,
                                                input_config)

    # Set rendering params
    define_camera.set_rendering_parameters(scene,
                                           input_config)

    # Insert camera keyframes
    define_camera.insert_camera_keyframes(camera_object,
                                          transforms_dict,
                                          input_config)


    ################################################
    # Save config used for rendering as json
    #############################################
    # create output dir if it doesnt exist
    if not os.path.exists(input_config.render_output_parent_dir_path):
        os.makedirs(input_config.render_output_parent_dir_path)

    # add json file with config info
    if input_config.flag_save_config_as_json:
        json_filename = os.path.join(input_config.render_output_parent_dir_path,
                                     input_config.render_output_parent_dir_str + '.json')
        with open(json_filename, 'w') as f:
            config_dict = input_config.__dict__
            for kr in input_config.keys_to_exclude_from_config_dict:
                config_dict.pop(kr, None)
            json.dump(config_dict, f)


if __name__ == '__main__':
    # Reminder:
    # name is main if it's not run as a module; this prevents from running the script when its not intended (e.g., when doing import 'main')
    # https://stackoverflow.com/questions/419163/what-does-if-name-main-do

    #################################
    # Python and Blender modules
    ####################################
    # Python modules
    import os
    import sys
    import argparse
    import numpy as np
    # import math
    # import pdb
    import json
    import importlib
    #import code
    #import IPython

    # Blender modules
    import bpy
    import mathutils
    import bmesh

    ##################################
    # Get Python command line args
    ##################################
    ## Get list of Python command line args
    argv = sys.argv
    if "--" not in argv:
        argv = []
    else:
        argv = argv[argv.index("--") + 1:]  # get all arguments after '--' (all after -- are not read by blender)

    ## Create parser object
    # When --help or no args are given, print this help
    usage_text = ("Run blender in background mode with this script:"
                  "  blender --background --python " + __file__ + " -- [path to json file with config input params] [options]")
    parser = argparse.ArgumentParser(description=usage_text)


    ## Add required argument: config_class_inputs [positional]
    parser.add_argument(
        "config_class_inputs_json",
        metavar='CONFIG_CLASS_INPUTS_JSON',  # A name for the argument in usage messages.
        help="Json file with input parameters to config class",
    )

    ## Add optional argument: modules_path
    parser.add_argument(
        "-mp", "--modules_path",
        dest="modules_path",
        metavar='MODULES_PATH',
        default=os.path.dirname(os.path.abspath(__file__)),  # it will use the parent dir to this script as default also if running from Blender text editor
        help="Path to config, data, geometry and camera modules",
    )

    ## Parse arguments
    args = parser.parse_args(argv)


    ###############################
    # Import custom modules
    # (http://web.purplefrog.com/~thoth/blender/python-cookbook/import-python.html)
    ###############################
    # Change path to find my modules (is there a better way to do this?)
    # print(os.getcwd())  # initially, cwd is: C:\Program Files\Blender Foundation\Blender 2.81
    dir = os.path.dirname(bpy.data.filepath)
    if not dir in sys.path:
        sys.path.append(dir)  # I think it adds the blender file path to the system path *for this session only*

    # Import my modules
    os.chdir(args.modules_path)
    import config
    import load_data
    import define_geometry
    import define_camera

    # Force a reload (in case I edit the source after I start the Blender session)
    importlib.reload(config)
    importlib.reload(load_data)
    importlib.reload(define_geometry)
    importlib.reload(define_camera)

    #############################################
    # Call main (sets up scene: geometry, camera and rendering params)
    #############################################
    main()
