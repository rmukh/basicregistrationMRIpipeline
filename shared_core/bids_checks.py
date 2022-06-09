import json
import os
import shutil
from pathlib import Path
from typing import Tuple, Optional

from bids.layout import BIDSLayout
from bids.exceptions import BIDSValidationError

from shared_core.utils import continuously_ask_user_yn


def get_filename(fn) -> str:
    fn = Path(fn)

    while fn.suffix in {'.nii', '.gz', '.json', 'bval', 'bvec', 'tsv'}:
        fn = fn.with_suffix('')

    return fn.stem


class BIDS:
    def __init__(self, work_dir, subjects) -> None:
        self.layout = None
        self.convert_to_bids = False
        self.bids_ok = False
        self.n_subjects_bids = 0

        self.work_dir = work_dir
        self.subjects = subjects
        self.bids_subjects = []

        self.nifti_files = self.find_nifti_files(self.work_dir)
        self.meta_files = self.find_meta_files(self.work_dir)

    @staticmethod
    def find_nifti_files(fld) -> list:
        # find all NIFTI files
        found = []
        for root, _, files in os.walk(fld):
            for file in files:
                if file.endswith(".nii.gz") or file.endswith(".nii"):
                    found.append(os.path.join(root, file))
        return found

    @staticmethod
    def find_meta_files(fld) -> list:
        # find all meta files (.json, .bval, .bvec)
        found = []
        for root, _, files in os.walk(fld):
            for file in files:
                if any(file.endswith(ext) for ext in [".json", ".bval", ".bvec"]):
                    found.append(os.path.join(root, file))
        return found

    def check_bids(self) -> None:
        print(f"Checking {self.work_dir} ...")
        self.convert_to_bids = False

        # do checks
        try:
            self.layout = BIDSLayout(self.work_dir, validate=True)
        except BIDSValidationError as e:
            if "dataset_description.json" in str(e):
                print("'dataset_description.json' is missing from project root. "
                      "Every valid BIDS dataset must have this file.")
                print("Probably your dataset is not valid BIDS dataset.")
                print("If your dataset is valid BIDS dataset, please create this file and try again.")
                print("Otherwise, do you want to try this pipeline to convert your dataset into a BIDS format?")
                yn = continuously_ask_user_yn()
                if yn == "y":
                    self.convert_to_bids = True
                else:
                    print("Please make your dataset valid BIDS dataset and try again.")
                    exit(0)

        if not self.convert_to_bids:
            self.bids_subjects = self.layout.get_subjects()
            self.n_subjects_bids = len(self.bids_subjects)

        if self.n_subjects_bids == 0 and len(self.nifti_files) > 1:
            print("We found NIFTI files in the provided input directory, but no subjects in the BIDS layout.")
            print("Do you want to try this pipeline to convert your dataset into a BIDS format?")
            yn = continuously_ask_user_yn()
            if yn == "y":
                self.convert_to_bids = True
            else:
                print("Please make your dataset valid BIDS dataset and try again.")
                exit(0)
        elif self.n_subjects_bids == 0 and len(self.nifti_files) < 2:
            print("We found no NIFTI or DICOM files!")
            print("Makesure that your input directory is not empty and rerun this pipeline.")
            exit(0)
        elif self.n_subjects_bids < len(self.subjects):
            print("Number of subjects in BIDS format is less than number of detected subjects in the input directory.")
            print("Please make sure that you have the correct BIDS layout.")
            print("If you want to continue processing only the detected subjects, please answer 'y'.")
            bids_ask = continuously_ask_user_yn()
            if bids_ask == "y":
                print("Continue processing only the detected subjects.")
                self.bids_ok = True
            else:
                print("Please make sure that you have the correct BIDS layout.")
                exit(0)
        elif self.n_subjects_bids > len(self.subjects):
            print("Number of subjects in BIDS format is more than number of detected subjects in the input directory.")
            print("Please make sure that you have the correct BIDS layout!")
            exit(0)
        else:
            print("Number of subjects in BIDS format is equal to number of detected subjects in the input directory.")
            print("OK BIDS format.")
            self.bids_ok = True

    def run_check(self) -> None:
        self.check_bids()

        if self.convert_to_bids:
            print("Converting to BIDS format...")
            print("Do you want to reorganize your dataset into BIDS format "
                  "within the input folder or specify a new one?")
            print("If you want to use the input folder, please answer 'y', "
                  "if you want another one, please specify the FULL absolute path.")
            option = input()
            if option.lower() == "y":
                bids_folder = self.work_dir
            else:
                bids_folder = os.path.abspath(option)
                try:
                    os.makedirs(bids_folder, exist_ok=True)
                except OSError:
                    print("The specified path is not a valid directory.")
                    print("Please rerun and specify valid directory.")
                    exit(0)

            self.work_dir = bids_folder
            print("What is the name of your dataset?")
            dataset_name = input("[My Dataset by default]: ")
            if dataset_name == "":
                dataset_name = "My Dataset"

            with open(os.path.join(bids_folder, "dataset_description.json"), "w") as f:
                f.write(json.dumps({"Name": dataset_name, "BIDSVersion": "1.6.0"}))
            print("We created a dataset_description.json file in the output directory {}"
                  "".format(os.path.join(bids_folder, "dataset_description.json")))

            print("We need to identify the imaging modalities in your dataset.")
            print("* you can specify multiple patters, separated by commas.")
            is_t1, t1_patterns = self.ask_modality("T1", "IR-SPGR, T1-SPGR, T1-FLAIR")
            is_t2, t2_patterns = self.ask_modality("T2", "T2_Star, inplaneT2")
            is_dwi, dwi_patterns = self.ask_modality("DWI", "DTI, DWI, DWI_b1000")

            new_subject_names = {}
            subjects_digits_len = len(str(len(self.subjects)))
            if subjects_digits_len == 1:
                subjects_digits_len = 2
            for ind, subj in enumerate(self.subjects, start=1):
                print(f"Processing subject {subj}")
                new_ind = str(ind).zfill(subjects_digits_len)
                new_sub = f"sub-{new_ind}"

                # fill mapping dict
                new_subject_names[new_sub] = subj

                # create subject folder structure with new name
                new_sub_folder = os.path.join(bids_folder, new_sub)
                os.makedirs(new_sub_folder, exist_ok=True)
                os.makedirs(os.path.join(new_sub_folder, "anat"), exist_ok=True)
                os.makedirs(os.path.join(new_sub_folder, "dwi"), exist_ok=True)

                # find MR images
                all_locals_t1 = []
                all_locals_t2 = []
                all_locals_dwi = []

                for f in self.nifti_files:
                    t1 = self.find_modality_for_subject(is_t1, t1_patterns, subj, f)
                    all_locals_t1.append(t1) if t1 is not None else None
                    t2 = self.find_modality_for_subject(is_t2, t2_patterns, subj, f)
                    all_locals_t2.append(t2) if t2 is not None else None
                    dwi = self.find_modality_for_subject(is_dwi, dwi_patterns, subj, f)
                    all_locals_dwi.append(dwi) if dwi is not None else None

                # copy images to new folder in BIDS format
                t1_name = self.copy_images_to_bids(all_locals_t1, "anat", new_sub_folder, subj,
                                                   new_sub + "_T1w.nii.gz")
                t2_name = self.copy_images_to_bids(all_locals_t2, "anat", new_sub_folder, subj,
                                                   new_sub + "_T2w.nii.gz")
                dwi_name = self.copy_images_to_bids(all_locals_dwi, "dwi", new_sub_folder, subj,
                                                    new_sub + "_dwi.nii.gz")

                # find metadata for MR images (.json and .bval/.bvec)
                # and copy metadata to new folder in BIDS format
                for f in self.meta_files:
                    if t1_name in f and "json" in f:
                        shutil.copy(f, os.path.join(new_sub_folder, "anat", new_sub + "_T1w.json"))
                    if t2_name in f and "json" in f:
                        shutil.copy(f, os.path.join(new_sub_folder, "anat", new_sub + "_T2w.json"))
                    if dwi_name in f and "json" in f:
                        shutil.copy(f, os.path.join(new_sub_folder, "dwi", new_sub + "_dwi.json"))
                    if dwi_name in f and "bval" in f:
                        shutil.copy(f, os.path.join(new_sub_folder, "dwi", new_sub + "_dwi.bval"))
                    if dwi_name in f and "bvec" in f:
                        shutil.copy(f, os.path.join(new_sub_folder, "dwi", new_sub + "_dwi.bvec"))

                # clean up
                shutil.rmtree(os.path.join(bids_folder, subj))

            print("T1 images will have a suffix '_T1w', T2 images will have a suffix '_T2w'"
                  " and DWI images will have a suffix '_dwi'.")
            with open(os.path.join(bids_folder, "mapping.json"), "w") as f:
                f.write(json.dumps(new_subject_names))
            print("We created a mapping.json file in the output directory {}"
                  "".format(os.path.join(bids_folder, "mapping.json")))
            print("You can use it to map the subject names from the BIDS format to the original names.")
            self.check_bids()

    @staticmethod
    def ask_modality(modality, pattern_examples) -> Tuple[bool, str]:
        is_modality = False
        patterns = None

        print(f"Do you have {modality} images?")
        ask = continuously_ask_user_yn()
        if ask == "y":
            is_modality = True
            print("Please specify any distinct pattern either in folder or file name")
            print(f"we can use to identify {modality} images. It can be {pattern_examples}, etc.")
            patterns = input(f"[{modality} by default]: ")
            if patterns == "":
                patterns = f"{modality}"
        return is_modality, patterns

    @staticmethod
    def find_modality_for_subject(is_used, patterns, subj, f) -> Optional[str]:
        if is_used:
            for pattern in patterns.split(","):
                if pattern.strip() in f and subj in f:
                    return f
        return None

    @staticmethod
    def copy_images_to_bids(all_locals, data_type, new_sub_folder, subj, fn_new) -> str:
        if len(all_locals) == 1:
            shutil.copy(all_locals[0], os.path.join(new_sub_folder, data_type, fn_new))
            return get_filename(all_locals[0])
        elif len(all_locals) == 0:
            print(f"No T1 images found for subject {subj}!")
            print("You would need to fix this manually, "
                  "otherwise this subject won't be processed in the pipeline!")
            return ""
        else:
            print(f"Multiple T1 images found for subject {subj}!")
            print("Please specify the index of which one you want to use.")
            for ind, f in enumerate(all_locals):
                print(f"{ind}: {f}")
            print("Please enter the index of the image you want to use.")
            while True:
                index_to_use = input()
                try:
                    index_to_use = int(index_to_use)
                except ValueError:
                    print("Enter valid int value")
                else:
                    break

            shutil.copy(all_locals[index_to_use], os.path.join(new_sub_folder, data_type, fn_new))
            return get_filename(all_locals[index_to_use])

    def is_bids(self) -> bool:
        return self.bids_ok

    def get_work_dir(self) -> str:
        return self.work_dir

    def get_bids_subjects(self) -> list:
        return self.bids_subjects
