# 🦅 Through hawks' eyes 🦅

This repo contains the supporting code for the paper [*Through Hawks’ Eyes: Synthetically Reconstructing the Visual Field of a Bird in Flight*](https://link.springer.com/article/10.1007/s11263-022-01733-2), published in March 2023 in the *International Journal of Computer Vision* and available  open-access.


## Overview
In this work, we describe a method to synthetically reconstruct the visual information available to a hawk during flight. We demonstrate our method by using it to investigate hawks' gaze startegy when swiftly avoiding obstacles 🚀 and when pursuing fast moving targets 🐀.

To achieve our goal, we combined several 🤖 computer vision 👁️ techniques: 
- We first tracked the birds' 3D head movements in flight, using a submilimeter-precision **marker-based motion capture system** sampling at 200 Hz in a 20 m x 6 m x 4 m flight arena. 

- Then, we **modelled the geometry** of the arena in [Blender](https://www.blender.org/) <a href="https://emoji.gg/emoji/8027-blender"><img src="https://cdn3.emoji.gg/emojis/8027-blender.png" width="24px" height="24px" alt="Blender"></a>, an open-source 3D modelling and rendering software package. For this we used basic geometric primitives 🔺 ⚪ 🟩 and also explored the possibility of combining these with **SLAM-captured meshes** for the more complex geometry 🏵️. We used **ArUco fiducial markers** 📍 to express the captured meshes in the coordinate system of the motion capture.

- Finally, we used the bird head pose data from the motion capture system to define **a virtual camera** 🎥 in Blender, representative of the bird's visual field 🌐 during flight. We used Blender's rendering engine to produce RGB, depth, semantic and optic flow maps over the full visual field of the bird, at every timestep in the trajectory. We used these synthetic data to investigate the birds' gaze strategy around obstacles and when pursuing moving targets.

A visual summary of this work (including links to cool supplementary videos ✨😎) can be found [here](https://drive.google.com/file/d/1HmnPG8llCPGxQonDWB9Vwobwin49WGWj/view?pli=1)

## Usage
The code in this repo *does not* constitute a stand-alone software package 📦 😬. 

Instead, it is intended to provide supporting information to replicate the results presented on the paper ✔️👍. 

Our aim is to provide transparency and promote reproducibility practices in research, but (for now!) we are not planning to develop it into a fully-fledged package. Nevertheless, we hope you can still find it useful for your research! 🔍 👩‍💻 🧑‍🔬

*Instructions and dependencies (incl Blender version) to be added soon.*

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
- This work was presented as a [poster](https://drive.google.com/file/d/1HmnPG8llCPGxQonDWB9Vwobwin49WGWj/view) in the CVPR workshop *CV4Animals* in June 2022 ([track III, number 22](https://sites.google.com/view/cv4animals/2022-accepted-papers)). 

- A previous effort was accepted as a [workshop paper](https://www.biorxiv.org/content/10.1101/2021.06.16.446415v1) the year before, and selected for one of the four oral presentations (CVPR workshop *CV4Animals* June 2021, [paper presentation IV](https://sites.google.com/view/cv4animals/2021-home)).

- This same work received the [Best Student Presentation Award](https://doi.org/10.1093/icb/icac122) at the SICB+ conference in January 2021, in the Division of Neurobiology, Neuroethology, and Sensory Biology (DNNSB). SICB+ was the virtual edition of the Society of Integrative and Comparative Biology conference.

## Contact
For any questions, suggestions or comments on the code in this repo, feel free to reach out via Github issues 🤓

For questions about the paper, feel free to contact the corresponding author 📧
