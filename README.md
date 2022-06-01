# Basic registration dMRI pipeline
The basic structural and diffusion MRI registration with pre-processing pipeline in Python.

# Usage
`main.py -i <input folder (BIDS format or DICOM files)> -co <output folder for converted files (if you need to convert from DICOM to NIFTI)> -o <output folder for registration>`

You can enable a debug mode by adding `-d`. In that case, the pipeline stops once any error happens.

By default, the pipeline will create a folder *derivatives/pipeline_registration* within the input BIDS directory to comply with BIDS format

# BIDS format
The pipeline will attempt to convert DICOM files to gzipped NIFTI file format with the highest compression and try to organize them based on the input dataset folder structure. The program will be asking you questions to determine folders or filenames responsible for different MRI modalities (T1, T2, DWI). However, if it doesn't work correctly, please make sure to organize your dataset in a BIDS format first and then re-run the program.
I can recommend a few utilities that might help you.
* [BIDScoin: Coin your imaging data to BIDS](https://github.com/Donders-Institute/bidscoin)
* [BIDSKIT](https://github.com/jmtyszka/bidskit)
* [dcm2bids](https://github.com/UNFmontreal/Dcm2Bids)
* [HeuDiConv](https://github.com/nipy/heudiconv)

# Requirements
For now, you have to install all the dependencies manually.

* Python 3.6 or later
* [nipype](https://nipype.readthedocs.io/en/latest/)
* [pybids](https://github.com/bids-standard/pybids)
* [dcm2nixx (optionally)](https://github.com/rordenlab/dcm2niix)
* [MRtrix3](https://www.mrtrix.org/)
* [ANTs](http://stnava.github.io/ANTs/)
* [FSL](https://fsl.fmrib.ox.ac.uk/)

I recommend building MRtrix3 from the source (https://mrtrix.readthedocs.io/en/latest/installation/build_from_source.html), but pre-build version should work as well.

I recommend to spend time and configure fsl with CUDA. It will save you a lot of time. The latest version of eddy is *eddy_cuda9.1* and requires CUDA 9.1. If you already have a CUDA of some other version, you can install 9.1 along with it. Just make sure you have added it to the $PATH and $LD_LIBRARY_PATH environment variables.
The details at https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/eddy/UsersGuide

## TODO
* [ ] Add registration from T1 to DWI
* [ ] Add registration between T1 and T2 only
* [ ] Add an option to disable certain artifacts removal steps
* [ ] Add a global configuration file
* [ ] Add packaging for the pipeline

# Notes
I've tested it with ADNI dataset. DICOM -> NIFTI -> BIDS works well.

You can find additional details here: https://rinatm.com/basic-dmri-registration-pipeline/
