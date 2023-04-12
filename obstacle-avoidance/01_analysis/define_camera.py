#  Author: Sofia Minano Gonzalez
#  Date: 14/10/2021
#  Last revision: 14/10/2021
#  Python version: 3.9 (Blender 2.93)
#  Copyright (c) 2021, Sofia Minano Gonzalez
#  All rights reserved.

import bpy
import mathutils
import numpy as np
import sys
import pdb


def create_camera(scene,
                  config):
    """
    Create camera object and set required params from config

    :param scene:
    :param config:
    :return: camera_object
    """
    # Initialise camera
    camera_object = initialise_camera(scene,
                                      config)
    # Set params from config
    camera_object = set_camera_parameters(camera_object,
                                          config)
    return camera_object

def initialise_camera(scene,
                      config):
    """
    Create camera object and set default translation and rotation to zero

    :param scene:
    :param config:
    :return: camera_object
    """
    # Set render engine to 'CYCLES' (to access appropriate cameras')
    scene.render.engine = 'CYCLES'

    # Create camera data-block and object
    camera_data = bpy.data.cameras.new(name='Camera')
    camera_object = bpy.data.objects.new('Camera',
                                         camera_data)

    # Link camera to the scene
    bpy.context.collection.objects.link(camera_object)

    ### Set camera default translation  to zero, and rotation to quaternion mode and unit quaternion
    camera_object.location = mathutils.Vector(config.ini_camera_location)
    camera_object.rotation_mode = 'QUATERNION'
    camera_object.rotation_quaternion = mathutils.Quaternion(config.ini_camera_rotation_quat)

    return camera_object


def set_camera_parameters(camera_object,
                          config):
    """
    Set parameters from config in input camera object

    Parameters:
    - camera type (typically panoramic)
    - lat/long boundaries
    - shift xy
    - clipping distance
    - sensor width and fit


    :param camera_object:
    :param config:
    :return: camera_object
    """

    # Set camera type (panoramic 360deg)
    camera_object.data.type = config.camera_type
    camera_object.data.cycles.panorama_type = config.camera_panorama_type

    # Set latitude and longitude boundaries if EQUIRECTANGULAR
    if camera_object.data.cycles.panorama_type == 'EQUIRECTANGULAR':
        camera_object.data.cycles.latitude_min = config.camera_latitude_min_max_in_rad[0]
        camera_object.data.cycles.latitude_max = config.camera_latitude_min_max_in_rad[1]
        camera_object.data.cycles.longitude_min = config.camera_longitude_min_max_in_rad[0]
        camera_object.data.cycles.longitude_max = config.camera_longitude_min_max_in_rad[1]

    # Set latitude and longitude boundaries if FISHEYE_EQUIDISTANT
    if camera_object.data.cycles.panorama_type == 'FISHEYE_EQUIDISTANT':
        camera_object.data.cycles.fisheye_fov = config.camera_fisheye_equidistant_FOV_in_rad

    # Set shift in x and y
    camera_object.data.shift_x = config.camera_shift_x_y[0]
    camera_object.data.shift_y = config.camera_shift_x_y[1]

    # Set clipping distance (start and end)
    camera_object.data.clip_start = config.camera_clip_start_end_in_m[0]
    camera_object.data.clip_end = config.camera_clip_start_end_in_m[1]

    # Set sensor width and fit
    camera_object.data.sensor_width = config.camera_sensor_width
    camera_object.data.sensor_fit = config.sensor_fit

    return camera_object


def set_rendering_parameters(scene,
                             config):
    """
    Set rendering parameters

    Parameters:
    - device
    - pixel resolution
    - rendering start/end frames and frame rate
    - passes
    - metadata stamps
    - output format

    :param scene:
    :param config:
    :return:
    """
    # Select device (GPU)
    scene.cycles.device = config.render_device

    # Set pixel filter: if BOX (preferred), pixel filtering is disabled
    scene.cycles.pixel_filter_type = config.pixel_filter_type

    # Pixel resolution
    scene.render.resolution_x = config.render_resolution_x_y_in_pixels[0]
    scene.render.resolution_y = config.render_resolution_x_y_in_pixels[1]
    # if config.render_resolution_x_y_in_pixels[0]/config.render_resolution_x_y_in_pixels[1] !=2:
    #     raise ValueError('x:y pixel resolution not 2:1')
    scene.render.resolution_percentage = config.render_resolution_percentage  # ojo important
    scene.render.pixel_aspect_x = config.render_pixel_aspect_x_y[0]
    scene.render.pixel_aspect_y = config.render_pixel_aspect_x_y[1]

    # Animation start/end frames and frame rate
    scene.frame_start = config.animation_frame_start_end[0]  # from csv...
    scene.frame_end = config.animation_frame_start_end[1]
    scene.frame_step = config.render_frame_step
    scene.render.fps = config.render_fps # I think this only applies if I render a video...

    # Set render passes: combined, Z, Object ID, Vector
    scene.view_layers["ViewLayer"].use_pass_combined = config.render_use_pass_combined
    scene.view_layers["ViewLayer"].use_pass_z = config.render_use_pass_z
    scene.view_layers["ViewLayer"].use_pass_object_index = config.render_use_pass_object_index
    scene.view_layers["ViewLayer"].use_pass_vector = config.render_use_pass_vector

    # Metadata stamps
    scene.render.use_stamp = config.render_use_stamp
    scene.render.use_stamp_time = config.render_use_stamp_time
    scene.render.use_stamp_date = config.render_use_stamp_date
    scene.render.use_stamp_render_time = config.render_use_stamp_render_time
    scene.render.use_stamp_frame = config.render_use_stamp_frame
    scene.render.use_stamp_scene = config.render_use_stamp_scene
    scene.render.use_stamp_filename = config.render_use_stamp_filename
    scene.render.use_stamp_camera = config.render_use_stamp_camera

    # Render output format
    scene.render.filepath = config.render_output_parent_dir_path
    scene.render.use_overwrite = config.render_use_overwrite
    scene.render.use_file_extension = config.render_use_file_extension
    scene.render.use_render_cache = config.render_use_render_cache
    scene.render.image_settings.file_format = config.render_output_file_format
    scene.render.image_settings.color_mode = config.render_image_color_mode
    scene.render.image_settings.color_depth = config.render_image_color_depth
    if config.render_output_file_format == 'OPEN_EXR_MULTILAYER':
        scene.render.image_settings.exr_codec = config.render_image_exr_codec
        scene.render.image_settings.use_preview = config.render_image_use_preview

    ##################################################################################################
    # Render outpt via nde
    # #----------------------------------------
    # ## Customize multilayer EXR channels with nodes
    # # following https://github.com/Cartucho/vision_blender/blob/1f46fbe4c32ba3b32e2818911a102f497f2375a9/addon_ground_truth_generation.py#L329
    # # Set overwrite in output tab (not sure if I unset it if it won't be overwrtten)
    # #scene.render.use_overwrite = config.render_use_overwrite
    #
    # # Set up nodes
    # scene.use_nodes = True
    # tree = scene.node_tree
    #
    # # Remove old nodes
    # for node in tree.nodes:
    #     tree.nodes.remove(node)
    #
    # #------------------------------------------------------
    # # # EXR AUTO SAVER -- doesnt work well
    # # # https://github.com/3d-io/Blender_Exr_auto-pass_saver
    # # bpy.ops.node.exr_pass_saver()
    #
    # #---------------------------------------------------------
    # ## Create render layers node
    # #rl = scene.node_tree.nodes["Render Layers"]
    # # bpy.ops.node.add_node(type="CompositorNodeRLayers", use_transform=True)
    # node_render_layers = tree.nodes.new("CompositorNodeRLayers")
    # #name = 'Render Layers' #node_render_layers.name = "node_render_layers"
    #
    # ## Create output node
    # #node_output = create_node(tree, "CompositorNodeOutputFile", "node_output")
    # #node_exists = check_if_node_exists(tree, node_name)
    # node_output = tree.nodes.new("CompositorNodeOutputFile")
    # #name = 'File Output' #node_output.name = "node_output"
    #
    # # add properties to output node
    # node_output.base_path = config.render_output_parent_dir_path # node_output.format.filepath = config.render_output_parent_dir_path
    # print(node_output.base_path)
    # # node_output.format.use_overwrite = config.render_use_overwrite
    # # node_output.format.use_file_extension = config.render_use_file_extension
    # # node_output.format.use_render_cache = config.render_use_render_cache
    # node_output.format.file_format = config.render_output_file_format
    # node_output.format.color_mode = config.render_image_color_mode
    # node_output.format.color_depth = config.render_image_color_depth
    # if config.render_output_file_format == 'OPEN_EXR_MULTILAYER':
    #     node_output.format.exr_codec = config.render_image_exr_codec
    #     #scene.render.image_settings.file_format = config.render_output_file_format
    #     #scene.render.filepath = config.render_output_parent_dir_path
    #     #scene.render.image_settings.use_preview = config.render_image_use_preview
    #
    #
    # ## Link nodes
    # node_output.layer_slots.clear()  # Remove all the default layer slots
    # links = tree.links
    #
    # # combined pass (always?)
    # slot_combined = node_output.layer_slots.new('View Layer.Combined')
    # links.new(node_render_layers.outputs['Image'], slot_combined)
    #
    # if config.render_use_pass_z:
    #     slot_depth = node_output.layer_slots.new('View Layer.Depth') #('####_Depth')
    #     links.new(node_render_layers.outputs['Depth'], slot_depth)
    # if config.render_use_pass_object_index:
    #     slot_seg_mask = node_output.layer_slots.new('View Layer.IndexOB')
    #     links.new(node_render_layers.outputs['IndexOB'], slot_seg_mask)
    # if config.render_use_pass_vector:
    #     # Create new slot in output node
    #     slot_opt_flow = node_output.layer_slots.new('View Layer.Vector')
    #     links.new(node_render_layers.outputs['Vector'],
    #               node_output.inputs['View Layer.Vector'])
    #
    #     # Get relevant components from optical flow
    #     # separate node: from image to RGBA
    #     node_rgba_separate = tree.nodes.new("CompositorNodeSepRGBA") #name: 'Separate RGBA', "BA_sep_vision_blender")
    #     # combine node: from RGBA to image
    #     node_rgba_combine = tree.nodes.new("CompositorNodeCombRGBA") # 'Combine RGBA', "RG_comb_vision_blender")
    #     # rename slots in combine
    #     # node_rgba_combine.layer_slots.clear()
    #     # node_rgba_combine.layer_slots.new('X')
    #     # node_rgba_combine.layer_slots.new('Y')
    #     # node_rgba_combine.layer_slots.new('Z')
    #     # node_rgba_combine.layer_slots.new('W')
    #     # link output of Render layers - Vector to input Separate RGBA input
    #     links.new(node_render_layers.outputs["Vector"],
    #               node_rgba_separate.inputs["Image"])
    #     # link all output Separate RGBA input to combine RGBA output
    #     # links.new(node_rgba_separate.outputs["R"],
    #     #           node_rgba_combine.inputs["R"])
    #     # links.new(node_rgba_separate.outputs["G"],
    #     #           node_rgba_combine.inputs["G"])
    #     links.new(node_rgba_separate.outputs["B"],
    #               node_rgba_combine.inputs["B"])
    #     links.new(node_rgba_separate.outputs["A"],
    #               node_rgba_combine.inputs["A"])
    #     # Connect to output node
    #     links.new(node_rgba_combine.outputs['Image'],
    #               slot_opt_flow)
    #
    # # if preview requiried: saved as png?---[not great, better to make a jpeg node]
    # if config.render_image_use_preview:
    #     scene.render.filepath = config.render_output_parent_dir_path


def insert_camera_keyframes(camera_object,
                            transforms_dict,
                            input_config):

    """
    Insert camera keyframes for translation and rotation

    - Gets quaternions to rotate Blender camera to desired initial pose, and to rotate headRF to eyesRF
    - Looping thru rendering frames:
        - insert translation keyframes as 'location' (use interp data if required)
        - insert rotation keyframe
            - get quaternions from csv data
            - add appropriate rotation quaternion to camera object.
                - Unless one of the flags for the special cases of the reference frame to track is True, the camera tracks the eyesRF (coord syst linked to the visual system)
            - insert keyframe
    - Set interpolation between all keyframes (Constant)
    - Set the scene camera to the camera object (otherwise Cycles won't find it)

    :param camera_object:
    :param transforms_dict:
    :param input_config:
    :return:
    """

    ######################################################################################################################################
    ### Compute quaternion to rotate Blender camera (applied first, same for all frames)
    eul_worldRF_to_cameraRF_rad = mathutils.Euler(input_config.eul_worldRF_to_cameraRF_rad[0],
                                                  input_config.eul_worldRF_to_cameraRF_rad[1])  # in rad!
    quat_worldRF_to_cameraRF = eul_worldRF_to_cameraRF_rad.to_quaternion()

    ### Compute quaternion to rotate headRF ref pose to eyesRF (same for all frames)
    quat_from_headRF_t0_to_eyesRF = \
        mathutils.Quaternion(input_config.eyesRF_quat_dict[input_config.date_bird_HP_pair_str])

    ####################################################################################################################################################3
    ### Insert keyframes at each frame
    for frame in range(input_config.animation_frame_start_end[0],
                       input_config.animation_frame_start_end[1] + 1):
        ### get idx for this frame
        idx_frame = np.where(transforms_dict['frame'] == frame)

        ####################################################################################################################################################3
        ### Insert translation keyframe (interp or not)
        if input_config.flag_use_transform_interp:
            camera_object.location = mathutils.Vector(
                transforms_dict['transform_t_interp_XYZ'][idx_frame].squeeze() * input_config.mm_to_m)
        else:
            camera_object.location = mathutils.Vector(
                transforms_dict['transform_t_XYZ'][idx_frame].squeeze() * input_config.mm_to_m)
        camera_object.keyframe_insert(data_path='location',
                                      frame=frame)

        ####################################################################################################################################################
        ### Insert rotation keyframe
        # Rotate camera to desired pose --apply rotation to camera first! (quat_worldRF_to_cameraRF)

        ### Get rotation quaternions from csv data
        # (rotation from ref pose to pose at t; ref pose is headpack axes aligned with world axes; interp or not)
        if input_config.flag_use_transform_interp:
            quat_from_transforms_csv = mathutils.Quaternion(
                transforms_dict['transform_q_interp_WXYZ'][idx_frame].squeeze())
        else:
            quat_from_transforms_csv = mathutils.Quaternion(
                transforms_dict['transform_q_WXYZ'][idx_frame].squeeze())

        ### Add the required rotation quaternion to camera object
        ### Opt 1: camera tracks trajectoryRF
        if input_config.flag_camera_tracks_trajectoryRF:
            # check if csv path for transforms contains 'trajectoryRF'! if not, exit
            if 'trajectoryRF' not in input_config.transforms_csv_path_to_file:
                sys.exit("ERROR in config: the transforms csv data path does not contain 'trajectoryRF', but flag_camera_tracks_trajectoryRF is set to True")
            camera_object.rotation_quaternion = quat_from_transforms_csv @ quat_worldRF_to_cameraRF

        ### Opt 2: camera tracks headRF (coordinate system linked to headpack)
        elif input_config.flag_camera_tracks_headRF:
            camera_object.rotation_quaternion = quat_from_transforms_csv @ quat_worldRF_to_cameraRF

        ### Opt 3: camera always parallel to worldRF
        elif input_config.flag_camera_tracks_worldRF:
            camera_object.rotation_quaternion = quat_worldRF_to_cameraRF

        ### Opt 4: camera tracks eyesRF (visual system linked coord system)
        # requires an additional rotation to eyesRF
        else:
            camera_object.rotation_quaternion = \
                    quat_from_transforms_csv @ quat_from_headRF_t0_to_eyesRF @ quat_worldRF_to_cameraRF # I think this is correct: quat_from_worldRF_to_headRF*quat_from_headRF_to_eyesRF * quat_worldRF_to_cameraRF

        # insert rotation keyframe
        camera_object.keyframe_insert("rotation_quaternion",
                                      frame=frame)

    #############################################################################################################################################################
    ## Set interpolation between keyframes
    # https://blender.stackexchange.com/questions/27157/how-to-change-to-constant-interpolation-mode-from-a-python-script
    list_of_fcurves = camera_object.animation_data.action.fcurves
    for fcurve in list_of_fcurves:
        for kf in fcurve.keyframe_points:
            kf.interpolation = input_config.interpolation_between_keyframes

    #############################################################################################################################################################
    ## Set the scene camera to the camera object
    # https://blender.stackexchange.com/questions/67805/bpy-ops-render-render-does-not-find-camera
    bpy.context.scene.camera = camera_object
