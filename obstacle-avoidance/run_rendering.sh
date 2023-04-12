#!/bin/bash

############################################################
# Batch rendering of trials
############################################################
#
# This script:
# - runs the Python-Blender script that sets up the Blender scene and defines the camera keyframes, for each input json file in the specified directory.
# - renders the scene using Cycles engine (either a selected range of frames (default) or the complete animation (if ran with -a, see details below))
#
#########################
# Optional inputs:
#########################
# Example command in terminal with all possible inputs (except help -h):
#   ./run_batch_rendering.sh -p "path/to/python/script" -j "path/to/input/jsons/dir" -b -a
#
# Description (see help function in code for further details):
#   -p: path to Blender-Python script.
#       If not specified, default is '/parent/directory/of/bash/script/main.py'
#
#   -j: path to directory with input json files
#       If not specified, default is empty ('') (it will fail)
#
#   -b: if present, Blender output to terminal is saved as a text file [recommended for debugging]
#
#   -a: If present, the whole animation is rendered, and the suggested range of frames for rendering specified in input json file per trial is ignored
#       [not recommended, it will produce a large output]
#
#   -h: prints help and syntax
#
########################
# Useful Blender commands
#######################
# (Assuming the 'blender' alias is defined)
#
#- To open GUI and wait for user input
#     blender --python "$PYTHON_SCRIPT_PATH" -- "$json_file";

#- To render the complete animation
#     blender --background --python "$PYTHON_SCRIPT_PATH" --render-anim -- "$json_file";
#
# - To render **one frame** (e.g. 900) and get output dir into variable (with grep reading the std out)
#     rendered_output_dir=$(blender --background --python "$PYTHON_SCRIPT_PATH" --render-frame 900 -- "$json_file"  | grep "Saved: " )
#
# - To render a non-continuous sequence of frames: use a comma-separated list (no spaces) and indicate continuous chunks with '..'
#     blender --background --python "$PYTHON_SCRIPT_PATH" --render-frame 714..1145,1922..2303 -- "$json_file"
#
#
############################################################
# Help function
############################################################
# https://www.redhat.com/sysadmin/arguments-options-bash-scripts
help()
{
   # Display Help
   echo "------------------------------------------------------"
   echo "Description"
   echo "------------------------------------------------------"
   echo "This script:"
   echo " - runs the Python-Blender script that sets up the Blender scene and defines the camera keyframes, for each input json file in the specified directory, and"
   echo " - renders the scene using Cycles engine, either a selected range of frames (default) or the complete animation (if ran with -a, see details below)."
   echo
   echo
   echo "------------------------------------------------------"
   echo "Syntax"
   echo "------------------------------------------------------"
   echo "run_rendering [-p|j|b|a|h]"
   echo
   echo "Options:"
   echo "    -p    <path/to/python/script>"
   echo "          Path to Blender-Python script."
   echo "          If not specified, default is './01_analysis/main.py'"
   echo
   echo "    -j    <path/to/dir/w/input/json/files>"
   echo "          Path to directory with input json files."
   echo "          If not specified, default is './00_data/config_input_files'"
   echo
   echo "    -b     If present, Blender's output to terminal is saved for each rendered trial. It is saved as a text file in the output render directory"
   echo "           LOG_<rendered_trial_str>"
   echo
   echo "    -a     If present, the whole animation is rendered, and the suggested range of frames specified in the input json file is ignored (not recommended)"
   echo "           (i.e., if -a, the blender command is ran with --render-anim, rather than --render-frame <suggested frame sequence from input json>)"
   echo
   echo "    -h     Print this Help."
   echo
}

######################################################################################
# Get input parameters
######################################################################################

### Initialise params with defaults
# Python path (default: directory where bash script is at)
BASH_SCRIPT_DIRECTORY=$(dirname "$0")
PYTHON_SCRIPT_PATH="$BASH_SCRIPT_DIRECTORY"/01_analysis/main.py

# Input json dir (default: empty)
INPUT_JSONS_DIR="$BASH_SCRIPT_DIRECTORY"/00_data/config_input_files

# initialise Blender log w false
flag_save_blender_log_to_txt_per_trial=false

# initialise flag for rendering the whole animation with false
# (if true, it will render the complete animation, from TO_1 to L_2, 
# ignoring the suggested range of frames for rendering specified in input json file)
flag_render_complete_animation=false

# (log of batch rendering terminal is always saved)


### Parse inputs
while getopts "p:j:bah" flag;do
    case $flag in

      p) # path to Blender-python script
        PYTHON_SCRIPT_PATH=$OPTARG ;;

      j) # path to directory with input json files
        INPUT_JSONS_DIR=$OPTARG ;;

      b) # whether to save the Blender printouts to the terminal in a txt file per trial
        flag_save_blender_log_to_txt_per_trial=true ;;

      a) # if this flag is present, it will render the complete animation ignoring the suggested range of frames in the input json file
        flag_render_complete_animation=true ;;

      h) # display help
        help
        exit ;;

      \?) # Invalid option
        echo "Error: Invalid option"
        exit ;;

    esac
done

#############################################################
# Set tmp file for batch rendering LOG
###########################################################
# Refs:
# https://ops.tips/gists/redirect-all-outputs-of-a-bash-script-to-a-file/
# https://superuser.com/questions/86915/force-bash-script-to-use-tee-without-piping-from-the-command-line

# Initialise tmp file with touch command
tmp_filename=$(mktemp /tmp/LOG_patata.XXXXXXXXXX) || { echo "Failed to create temp file"; exit 1; } #makes a temporary unique filenname
touch "$tmp_filename" # touch command: It is used to create a file without any content.

# Set stdout to dump on tmp file
exec 1> >(tee "$tmp_filename")

# Redirect standard error to standard out
exec 2>&1 # (the order matters! if I do this first I am not sending stderr to file)


#############################################################
# Print batch rendering settings
###########################################################
echo "------------------------------------------------------"
echo "Batch rendering settings"
echo "$(date +%x) $(date +%T)" #format: dd/mm/yy HH:MM:SS
echo "------------------------------------------------------"
echo "* Python script path: $PYTHON_SCRIPT_PATH";
echo "* Input jsons directory: $INPUT_JSONS_DIR";
echo ""
echo
echo "* Save Blender log to txt file per trial: $flag_save_blender_log_to_txt_per_trial";
echo
echo "* Render complete animation: $flag_render_complete_animation";


##############################################################################################
# Run Blender-Python script per trial
##############################################################################################

echo "------------------------------------------------------"
echo "Start rendering..."
echo "------------------------------------------------------"

# initialise parameters for the batch rendering log file
timestamp=$(date '+%Y%m%d%H%M')  # get timestamp before any rendering
c=0

# initialise list of paths to the directories of successfully rendered trials
list_of_dirpaths_of_succesfully_rendered_trials=()
n_valid_input_json_files=0

# Loop thru json files only (excludes folders), not recursive
for json_file in "$INPUT_JSONS_DIR"/*.json;
  do
    #################################################################################
    # If it is a file, and doesn't start with 'template': render
    #################################################################################
    if [ -f "$json_file" ] && [[ "$json_file" != *"template_dict_"*.json ]]; then

        # Get trial string from input json (I use it to print it to terminal)
        trial_str=$(jq ".trial_str" "$json_file")
        ((n_valid_input_json_files+=1)) #arithmetic expansion

		    #####################################################################
        # Render animation  (main command)
        #####################################################################
        # If flag -a present: render complete animation
        #####################################################################
        if [[ "$flag_render_complete_animation" = true ]]; then

            # Run blender with --render-anim and get printout in variable
            echo "* Rendering full animation for $trial_str"
            blender_output_to_terminal=$(blender --background --python "$PYTHON_SCRIPT_PATH" --render-anim -- "$json_file")

            # Get exit status of rendering operation
            status_rendered_output=$?

        ##############################################################################
        # If flag -a absent: render the range of frames suggested in input json file
        ##############################################################################
        # (a warning is printed from python script if this suggested range of frame does not match TO-L frames per leg, for the selected trial)
        else

            # Get suggested range of frames to render from input json
            # leg 1
            FRAME_TO_1=$(jq ".suggested_frame_range_for_cli_rendering_leg_1[0]" "$json_file") #typically FRAME_TO_1
            FRAME_L_1=$(jq ".suggested_frame_range_for_cli_rendering_leg_1[1]" "$json_file")  #typically FRAME_L_1
            # leg 2
            FRAME_TO_2=$(jq ".suggested_frame_range_for_cli_rendering_leg_2[0]" "$json_file") #typically FRAME_TO_2
            FRAME_L_2=$(jq ".suggested_frame_range_for_cli_rendering_leg_2[1]" "$json_file") #typically FRAME_L_2


            # Run blender with --render-frame <suggested range of frames> and get blender printout in variable
            echo "* Rendering the following range of frames for $trial_str: $FRAME_TO_1..$FRAME_L_1,$FRAME_TO_2..$FRAME_L_2"
            blender_output_to_terminal=$(blender --background --python "$PYTHON_SCRIPT_PATH" --render-frame $FRAME_TO_1..$FRAME_L_1,$FRAME_TO_2..$FRAME_L_2 -- "$json_file")

            # Get exit status of rendering operation
            status_rendered_output=$?

        fi


        #######################################################################
        # Get render output directory path and batch rendering dir
        #######################################################################
        # Get line with 'Saved:' from Blender output
        # use m1 to exit after first match! 
        # ATT! this is because if we are saving preview as well, there will be two lines starting with 'Saved:'
        blender_output_saved_line=$( grep -m1 "Saved: " <<< "$blender_output_to_terminal" )

        # Get render output directory (path and basename); parentdir = trial subdirectory
        trial_subdir_fullpath="/${blender_output_saved_line#*/}" # removes everything up to the 1st slash(+prepends / to replace the one stripped) (#: left truncate after pattern)
        trial_subdir_fullpath="${trial_subdir_fullpath%/*}" # removes everything from the last fwd slash (%: right truncate following pattern)
        trial_subdir_str="${trial_subdir_fullpath##*/}" # take everything from last forward slash (##: left truncate all consecutive pattern matches from the left)

        # Get batch rendering directory
        batch_rendering_dir_fullpath=$(dirname "$trial_subdir_fullpath")
        batch_rendering_dir_str="${batch_rendering_dir_fullpath##*/}"

        # ATT! if trial_subdir = tmp or empty: set status of render operation as 1000
        if [[ $trial_subdir_str == "tmp" || $trial_subdir_str == "" ]]; then
             status_rendered_output=1000
        fi

        # Compute filename for batch rendering LOG file, for the first successful rendered trial
        # ATT! batch rendering stdout and stderr are in tmp file until copied at the end of the code
        if [[ $c -eq 0 ]] && [[ $status_rendered_output -eq 0 ]] ; then # only the first time
          batch_log_at_ssd_fullpath="$(dirname "$trial_subdir_fullpath")"/"LOG_$batch_rendering_dir_str"_$timestamp.txt

          # only do once!
          c=1
        fi

        ##############################################################################
        # Check status of rendering operation
        ##############################################################################
        # check status (if 0: successful)
        if [ $status_rendered_output -ne 0 ]; then
             # If unsuccessful, print warning
             echo "** [$(date +%T)]: FAILED rendering $trial_subdir_str"

        else

             # If successful, get rendered output directory from terminal output and append to list
             echo "* [$(date +%T)]: $trial_subdir_str saved at $(dirname "$trial_subdir_fullpath")"

             # append to list of rendered output dirs (is there a better way of doingn this?)
             list_of_dirpaths_of_succesfully_rendered_trials+=("$trial_subdir_fullpath")

        fi


        #######################################################################
        # If required: Save Blender stdout to LOG file for this trial
        #######################################################################
        # Get LOG file name from output dir
        if [ "$flag_save_blender_log_to_txt_per_trial" = true ]; then

            # Save blender output to log file
            echo "$blender_output_to_terminal" > "$trial_subdir_fullpath/LOG_$trial_subdir_str.txt"
            status_blender_log=$?

            # Check Blender LOG saving status
            if [ $status_blender_log -ne 0 ]; then
                 # If unsuccessful, print warning
                 echo "** [$(date +%T)]: FAILED saving Blender LOG for $trial_subdir_str"
                 echo " "
            else
                 # If successful, get rendered output directory from terminal output and append to list
                 echo "* [$(date +%T)]: $trial_subdir_str Blender LOG saved "
                 echo " "

            fi
        fi

    #################################################################################
    # If file starts with 'template': print warning
    #################################################################################
    else
        echo ""
        echo "WARNING: ${json_file##*/} is not a valid input json file, skipped"
    fi

  done

############################################################################################
# Print number of succesfully rendered trials, relative to trials with valid json file
############################################################################################
echo
echo "Successfully rendered trials (over total input json files): ${#list_of_dirpaths_of_succesfully_rendered_trials[@]}/"$n_valid_input_json_files" "
echo ""


###########################################################
# Copy batch rendering LOG file to local if required
###########################################################
cp "$tmp_filename" "$batch_log_at_ssd_fullpath"
status_batch_log_to_local_ssd=$?

###########################################################################
# Delete tmp file (if saved to any of the previous ones)
###########################################################################
# https://tldp.org/LDP/abs/html/comparison-ops.html
# https://stackoverflow.com/questions/40430770/bash-what-does-eq-mean
if [[ "$status_batch_log_to_local_ssd" -eq 0 ]] ; then
  rm "$tmp_filename"
fi