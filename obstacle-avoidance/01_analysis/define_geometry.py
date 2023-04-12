#  Author: Sofia Minano Gonzalez
#  Date: 14/10/2021
#  Last revision: 14/10/2021
#  Python version: 3.9 (Blender 2.93)
#  Copyright (c) 2021, Sofia Minano Gonzalez
#  All rights reserved.

import math
import numpy as np
import bpy
import pdb


def create_environment(geometry_dict,
                       config):
    """
    Creates the lab environment
    This involves
     - Removing objects by default in scene,
     - building perches, obstacles, and planes (walls, floor, ceiling),
     - adding lamps of type SUN

    :param geometry_dict:
    :param config:
    :return:
    """
    ##########################################################################################3
    ### Remove pre-existing objects
    # (in default startup blend file: camera, light and cube)
    # https://docs.blender.org/api/current/bpy.ops.html#overriding-context
    context_copy = bpy.context.copy()
    context_copy['selected_objects'] = list(bpy.context.scene.objects)
    bpy.ops.object.delete(context_copy)

    ### Delete pre-existing data blocks
    # (if running the code several times in Blender, some data accumulate)
    # remove cameras, materials, meshes, lights and actions from several runs (not sure this is the best way)
    [bpy.data.cameras.remove(e) for e in bpy.data.cameras]
    [bpy.data.materials.remove(e) for e in bpy.data.materials]
    [bpy.data.meshes.remove(e) for e in bpy.data.meshes]
    [bpy.data.lights.remove(e) for e in bpy.data.lights]
    [bpy.data.actions.remove(e) for e in bpy.data.actions]

    ##########################################################################################3
    ### Build perches (cylinders)
    list_edges_str_all_perches = [k for k in geometry_dict.keys() if 'perch' in k]
    list_perches_start = list(set([e_i[0:9] for e_i in list_edges_str_all_perches]))
    for perch_str in list_perches_start:
        perch_object = create_cylinder_between_points(
                                                        (geometry_dict[perch_str + '_xmax_edge_centroid_XYZ'][0:3]
                                                         - np.array([0, 0, config.perch_marker_centre_to_cyl_axis_z_offset])) * config.mm_to_m,
                                                        (geometry_dict[perch_str + '_xmin_edge_centroid_XYZ'][0:3]
                                                         - np.array([0, 0, config.perch_marker_centre_to_cyl_axis_z_offset])) * config.mm_to_m,
                                                        config.perch_radius * config.mm_to_m)
        # assign name
        perch_object.name = perch_str

        # assign object index
        perch_object.pass_index = config.dict_perch_str_to_object_index[perch_object.name]

    ##########################################################################################3
    ### Build obstacles (cylinders)
    # if not all coords nan, for at least one obs: aim to reconstruct
    if any([not (all(np.isnan(geometry_dict[k])))
            for k in geometry_dict.keys() if 'obs' in k]):

        for i, obs_str in enumerate([k for k in geometry_dict.keys() if 'obs' in k]):
            # Build cylinder between top obs marker (considering offset), and its projection in z=0
            top_obs_marker = geometry_dict[obs_str][:] - np.array([0, 0, config.marker_centre_to_top_obs_base])
            bottom_obs_marker = np.concatenate((top_obs_marker[0:2], 0.0), axis=None)
            obs_object = create_cylinder_between_points(tuple(top_obs_marker * config.mm_to_m),
                                                        tuple(bottom_obs_marker * config.mm_to_m),
                                                        config.obs_radius * config.mm_to_m)
            # assign name
            obs_object.name = obs_str[0:[i for i, p in enumerate(obs_str) if p == '_'][2]]  # bpy.context.object.name = obs_str[0:[i for i, p in enumerate(obs_str) if p == '_'][2]]

            # assign object index
            if config.flag_use_obstacle_ID_as_object_index:
                for s in obs_str.split('_'):
                    if s.isdigit():
                        obs_object.pass_index = int(s)
            else:
                obs_object.pass_index = config.dict_obs_ID_to_object_index[obs_object.name]

    ##########################################################################################3
    ### Build walls, floor and ceiling (planes)
    list_of_vertices_str_all_planes = [k for k in geometry_dict.keys()
                                       if 'wall' in k or 'floor' in k or 'ceiling' in k]
    list_of_planes_start_str = list(set([v_i[0:-1] for v_i in list_of_vertices_str_all_planes]))
    for p_str in list_of_planes_start_str:
        # Build plane
        vertices = [tuple(geometry_dict[p_str + str(kk)] * config.mm_to_m)
                    for kk in range(1, config.n_vertices_per_plane + 1)]
        plane_object = create_plane_between_vertices(vertices)

        # assign name
        plane_object.name = p_str[0:[i for i, p in enumerate(p_str) if p == '_'][-2]]

        # assign object index----
        plane_object.pass_index = config.dict_planes_str_to_object_index[plane_object.name]

        # set origin to centre of surface
        plane_object.select_set(True)
        bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_MASS',
                                  center='MEDIAN')
        plane_object.select_set(False)

    ##########################################################################################3
    ### Add lamps of type 'SUN' (light)
    list_tuples_location_lamps_in_m = list()
    for loc_tuple in config.list_tuples_location_lamps_in_mm:
        list_tuples_location_lamps_in_m.append(tuple([x * config.mm_to_m for x in loc_tuple]))

    create_lamps_wo_shadow(list_tuples_location_lamps_in_m,
                           config.list_tuples_rotation_euler_lamps_in_rad,
                           config.list_lamps_strength)

    ##########################################################################################3
    ### Assign materials to objects
    # https://blender.stackexchange.com/questions/56751/add-material-and-apply-diffuse-color-via-python
    for obj in list(bpy.data.objects):
        if obj.name in config.dict_geometry_to_material_hex_str_and_alpha.keys():
            # create material for this object
            mat = bpy.data.materials.new(name='material_' + obj.name)

            # get RGB-ALPHA from HEX color for this object
            hex_num = int(config.dict_geometry_to_material_hex_str_and_alpha[obj.name][0],
                          16)
            rgba_from_hex = hex_to_rgb(hex_num,
                                       config.dict_geometry_to_material_hex_str_and_alpha[obj.name][1])

            # add RGB-A to material
            mat.diffuse_color = rgba_from_hex

            # add material to object
            obj.data.materials.append(mat)

            # unselect object
            obj.select_set(False)


def create_cylinder_between_points(P1, P2, R):
    """
    Create cylinder from coordinates of bases' centres and radius

    Create cylinder with bases' centres at P1 and P2, and radius R
    P1 and P2 passed as numpy array

    Based on script from: https://blender.stackexchange.com/questions/5898/how-can-i-create-a-cylinder-linking-two-points-with-python

    :param P1: centre of one of the bases
    :param P2: centre of another one of the bases
    :param R: radius
    :return: cylinder_object
    """

    # Parse coordinates of centres
    x1, y1, z1 = P1
    x2, y2, z2 = P2

    # Add cylinder between those centre points
    dx = x2 - x1
    dy = y2 - y1
    dz = z2 - z1
    dist_btw_centres = math.sqrt(dx ** 2 + dy ** 2 + dz ** 2)
    bpy.ops.mesh.primitive_cylinder_add(
        radius=R,
        depth=dist_btw_centres,
        location=(x1 + dx/2,
                  y1 + dy/2,
                  z1 + dz/2)
    )

    # Set at appropriate orientation (perp to XY plane)
    # (angles defining axis orientation: phi theta)
    phi = math.atan2(dy, dx)  # angle between line connecting bases centres', projected on XY plane, and the world X axis
    theta = math.acos(dz / dist_btw_centres)  # angle of cylinder axis with its base
    bpy.context.object.rotation_euler[1] = theta # rotation around x axis? (when creating a cylinder, bases parallel to XY global plane)
    bpy.context.object.rotation_euler[2] = phi

    # Return cylinder object (active because just created)
    cylinder_object = bpy.context.object
    return cylinder_object

def create_plane_between_vertices(verts):
    """
    Create plane from 4 vertices
    :param verts: list of tuples of coords (X,Y,Z) per vertex
    :return:
    """
    # Define mesh and object variables
    blender_mesh = bpy.data.meshes.new("Plane")
    blender_object = bpy.data.objects.new("Plane",
                                          blender_mesh)

    # Set location and scene of object
    blender_object.location = [0, 0, 0]

    # Link object to current collection
    # after API change in 2.80, we no longer link object to the scene, but to collections https://blender.stackexchange.com/questions/145658/link-new-object-to-scene-with-python-in-2-8
    bpy.context.collection.objects.link(blender_object)


    # Create mesh
    faces = [(0, 1, 2, 3)]
    blender_mesh.from_pydata(verts,
                             [],
                             faces)
    blender_mesh.update(calc_edges=True)

    return blender_object


def create_lamps_wo_shadow(list_tuples_location,
                           list_tuples_rotation_euler_in_rad,
                           list_strengths):
    """
    Create lamps of type SUN, at specified location, and of specified energy


    :param list_tuples_location: list of tuples for each lamp location
    :param list_tuples_rotation_euler_in_rad: list of tuples for each lamp orientation
    :param list_strengths: list of strengths for each lamp
    :return: list_of_lamp_objects
    """
    scene = bpy.context.scene
    n_lamps = len(list_tuples_location)
    list_of_lamp_objects = []
    for i in range(n_lamps):
        # Create new lamp datablock and object
        lamp_data = bpy.data.lights.new(name="Lamp_" + str(i), type='SUN')
        lamp_object = bpy.data.objects.new(name="Lamp_" + str(i), object_data=lamp_data)

        # Link lamp object to the scene
        bpy.context.collection.objects.link(lamp_object)

        # Specify lamp location and orientation
        lamp_object.location = list_tuples_location[i]
        lamp_object.rotation_euler = list_tuples_rotation_euler_in_rad[i]

        # Specify lamp energy
        # lamp_data.energy = list_energy[i]  # 0.7
        lamp_data.use_nodes = True
        lamp_data.node_tree.nodes['Emission'].inputs['Strength'].default_value = list_strengths[i]

        # Remove shadow for cycles
        lamp_data.cycles.cast_shadow = False

        # Append to list
        list_of_lamp_objects.append(lamp_object)

    return list_of_lamp_objects

# Hex to RGB functions for defining material
# https://blender.stackexchange.com/questions/158896/how-set-hex-in-rgb-node-python?noredirect=1#comment269316_158896
def srgb_to_linearrgb(c):
    if c < 0:
        return 0
    elif c < 0.04045:
        return c / 12.92
    else:
        return ((c + 0.055) / 1.055) ** 2.4


def hex_to_rgb(h,
               alpha=1):
    r = (h & 0xff0000) >> 16
    g = (h & 0x00ff00) >> 8
    b = (h & 0x0000ff)
    return tuple([srgb_to_linearrgb(c / 0xff) for c in (r, g, b)] + [alpha])


