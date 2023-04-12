# 🦅 Through hawks' eyes 🦅

This repo contains the supporting code for the paper [*Through Hawks’ Eyes: Synthetically Reconstructing the Visual Field of a Bird in Flight*](https://link.springer.com/article/10.1007/s11263-022-01733-2) (*International Journal of Computer Vision*, March 2023)

## Background
In the paper, we describe a method to synthetically reconstruct the visual information available to a hawk during flight. We demonstrate our method by using it to investigate hawks' gaze startegies when swiftly avoiding obstacles 🚀 and when pursuing fast moving targets 🐀.

To achieve our goal, we combined several 🤖 computer vision 👁️ techniques: 
- We first tracked the birds' 3D head movements in flight, using a submilimeter-precision **marker-based motion capture system** sampling at 200 Hz in a 20 m x 6 m x 4 m flight arena. 

- Then, we **modelled the geometry** of the arena in [Blender](https://www.blender.org/) <a href="https://emoji.gg/emoji/8027-blender"><img src="https://cdn3.emoji.gg/emojis/8027-blender.png" width="24px" height="24px" alt="Blender"></a>, an open-source 3D modelling and rendering software package. For this we used basic geometric primitives 🔺 ⚪ 🟩 and explored the possibility of combining these with **SLAM-captured meshes** for the more complex geometry 🏵️. We used **ArUco fiducial markers** 📍 to express the captured meshes in the coordinate system of the motion capture.

- Finally, we used the bird head pose data from the motion capture system to define **a virtual camera** 🎥 in Blender, representative of the bird's visual field 🌐 during flight. We used Blender's rendering engine to produce RGB, depth, semantic and optic flow maps over the full visual field of the bird, at every timestep in the trajectory. We used these synthetic data to investigate the birds' gaze strategy around obstacles and when pursuing moving targets.

Check out this [visual summary of our work!](https://drive.google.com/file/d/1HmnPG8llCPGxQonDWB9Vwobwin49WGWj/view?pli=1) Includes links to cool supplementary videos ✨😎

## Repo overview
The code in this repo:
1. sets up a scene in Blender, which consists on a 3D geometry and a 360 virtual camera with a specific animation, and 
2. renders RGB, depth, optic flow and semantic data from the perspective of the virtual camera as OpenEXR files.

The code in this repo *does not* constitute a stand-alone software package 📦 😬. 

Instead, it is intended to provide supporting information to replicate the results presented on the paper ✔️👍. 

Our aim is to provide transparency and promote reproducibility practices in research, but (for now!) we are not planning to develop it into a fully-fledged package. Nevertheless, we hope you can still find it useful for your research! 🔍 👩‍💻 🧑‍🔬


## Repo structure and workflow
*To be completed soon!*




## Usage

To setup the scenes and render the view from a virtual camera representing the birds' visual fields, follow the steps below. These have been tested in an Apple M2 laptop and for Blender 3.5.0.

Note that we use the Python interpreter included in the Blender package.

1. Add a Blender alias for your terminal following the instructions [here](https://docs.blender.org/manual/en/3.4/advanced/command_line/launch/index.html).

    In mac, you may need to run
    ```
    eval /usr/libexec/path_helper -s
    ``` 
    and restart the terminal for it to work

2. Run one of the following commands from the repo's topmost directory:

    - To open the Blender GUI and wait for user input (that is, the animation or rendering won't start automatically):
      ```
      blender --python "$PYTHON_SCRIPT_PATH" -- "$JSON_FILE"
      ```
      For the specific case of the sample obstacle avoidance flight, with the camera aligned with the bird's visual coordinate system, we would run:
      ```
      blender --python "./obstacle-avoidance/01_analysis/main.py" -- "../00_data/config_input_files/201124_Drogon16_eyesRF.json"
      ```
      Note that the double dash after the Python script path separates the Blender command line arguments and the Python script's arguments.

    - To render the complete animation, running Blender headless (i.e., no GUI. This is specified with the `--background` flag):
      ```
      blender --background --python "$PYTHON_SCRIPT_PATH" --render-anim -- "$JSON_FILE"
      ```

    - To render one frame (e.g. 900) and get the output directory into the `rendered_output_dir` variable:
      ```
      rendered_output_dir=$(blender --background --python "$PYTHON_SCRIPT_PATH" --render-frame 900 -- "$JSON_FILE"  | grep "Saved: " )
      ```

    - To render a non-continuous sequence of frames: use a comma-separated list (no spaces) and indicate continuous chunks with '..'
      ```
      blender --background --python "$PYTHON_SCRIPT_PATH" --render-frame 714..1145,1922..2303 -- "$JSON_FILE"
      ```


## How to read OpenEXR files in Matlab?
Although not included as part of this repo, the output OpenEXR files containing RGB, depth, semantic and optic flow data were analysed later in Matlab. 

In Matlab R2022b, the Image Processing Toolbox included for the first time [EXR reading and writing capabilities](https://uk.mathworks.com/matlabcentral/answers/611336-installing-openexr-in-matlab#answer_1059580). 

If you are using earlier versions of Matlab, you may find [these instructions](https://uk.mathworks.com/matlabcentral/answers/611336-installing-openexr-in-matlab#answer_653567) useful. They make use of the Matlab-OpenEXR bindings provided [here](https://github.com/skycaptain/openexr-matlab)


## Citation
If you find this code useful for your work, please cite us! 🤩

### *To cite the paper:*
APA style:
> *Miñano, S., Golodetz, S., Cavallari, T., & Taylor, G. K. (2023). Through hawks’ eyes: synthetically reconstructing the visual field of a bird in flight. International Journal of Computer Vision, 1-35.*

BibTeX:
```
@article{minano2023through,
  title={Through hawks’ eyes: synthetically reconstructing the visual field of a bird in flight},
  author={Mi{\~n}ano, Sof{\'\i}a and Golodetz, Stuart and Cavallari, Tommaso and Taylor, Graham K},
  journal={International Journal of Computer Vision},
  pages={1--35},
  year={2023},
  url={https://link.springer.com/article/10.1007/s11263-022-01733-2}
  publisher={Springer}
}
```

### *To cite this repo:*

For now, please use the following (DOI will be available soon!):

> *Minano, S. (2023) Through hawks’ eyes. GitHub repository. Retrieved from [https://github.com/sfmig/hawk-eyes](https://github.com/sfmig/hawk-eyes)*
 

## Related work
- This work was presented as a 🪧 [poster](https://drive.google.com/file/d/1HmnPG8llCPGxQonDWB9Vwobwin49WGWj/view) 🪧 in the CVPR workshop *CV4Animals* in June 2022 ([track III, number 22](https://sites.google.com/view/cv4animals/2022-accepted-papers)). 

- A previous effort was accepted as a 📜 [workshop paper](https://www.biorxiv.org/content/10.1101/2021.06.16.446415v1) 📜 the year before, and selected as one of the four oral presentations 🗣️ (CVPR workshop *CV4Animals* June 2021, [paper presentation IV](https://sites.google.com/view/cv4animals/2021-home)).

- This same work received the 🏆 [Best Student Presentation Award](https://doi.org/10.1093/icb/icac122) 🏆 at the SICB+ conference in January 2022, in the Division of Neurobiology, Neuroethology, and Sensory Biology (DNNSB). SICB+ was the virtual edition of the Society of Integrative and Comparative Biology conference.

## Contact
For any questions, suggestions or comments on the code in this repo, feel free to reach out via Github issues 🤓

For questions about the paper, feel free to contact the corresponding author 📧
