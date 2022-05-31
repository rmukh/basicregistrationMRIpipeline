import glob
import os

from nipype.interfaces.dcm2nii import Dcm2niix


class DICOM:
    def __init__(self, args, raw_subjects):
        self.args = args
        self.raw_subjects = raw_subjects

        # init variables
        self.converter = Dcm2niix()
        self.converter.inputs.out_filename = "%t"
        self.converter.inputs.compress = 'y'
        self.converter.inputs.compression = 9
        self.converter.inputs.verbose = False

        self.all_dicom_files = []
        self.partial_conversion = False
        self.ask_convert = "y"

        # run the conversion
        self.dicom_subjects = self.__dicom_subjects()
        self.__deal_partial()

    def __dicom_subjects(self):
        # find the subjects that contain dicom files
        dicom_subjects = []
        for subject in self.raw_subjects:
            fn = glob.glob(os.path.join(self.args.input, subject, "**/*.dcm"), recursive=True)
            self.all_dicom_files.extend(fn)
            if fn:
                dicom_subjects.append(subject)
        return dicom_subjects

    def __deal_partial(self):
        if len(self.dicom_subjects) > 0:
            print("Found {} subjects with dicom files".format(len(self.dicom_subjects)))
            print("Subjects with dicom files: {}".format(self.dicom_subjects))

            if len(self.dicom_subjects) != len(self.raw_subjects):
                # deal with a scenario when some the files are converted and some are not
                print("The number of original subjects and the number of subjects with dicom files do not match!")
                self.ask_convert = input(f"Convert all dicom files to nifti and store them in the "
                                         f"original folder: {self.args.input}? (y/n): ")
                self.partial_conversion = True

    def run_conversion(self):
        if len(self.dicom_subjects) > 0:
            if self.ask_convert.lower() == "n":
                print("Please, deal with the conversion manually and rerun the script.")
                exit(0)
            elif self.ask_convert.lower() == "y":
                print("Converting dicom files to nifti...")
                mri_images = []

                # find the most deep directory within every subject
                # to preserver the original directory structure
                for subject in self.dicom_subjects:
                    for currentpath, folders, _ in os.walk(os.path.join(self.args.input, subject), topdown=True):
                        if not folders:
                            subpath = os.path.relpath(currentpath, os.path.join(self.args.input, subject))
                            mri_images.append(os.path.join(subject, subpath))

                # iterate over all dicom files with a preserved structure and convert them to nifti
                for image in mri_images:
                    self.converter.inputs.source_dir = os.path.join(self.args.input, image)
                    if self.partial_conversion:
                        self.converter.inputs.output_dir = os.path.join(self.args.input, image)
                    else:
                        if not os.path.exists(os.path.join(self.args.converted_output, image)):
                            os.makedirs(os.path.join(self.args.converted_output, image))
                        self.converter.inputs.output_dir = os.path.join(self.args.converted_output, image)

                    try:
                        self.converter.run()
                    except OSError as e:
                        if "No command" in str(e):
                            self.__install_dcm2niix()
                            exit(0)
                print("Finished converting dicom files to nifti.")
            else:
                print("Please, enter y or n.")
                exit(0)

            # delete the dicom files?
            ask_delete = input("Delete DICOM files? (y/n): ")
            if ask_delete.lower() == "y":
                self.delete_dicoms(self.all_dicom_files)

            if self.partial_conversion:
                return self.args.input
            else:
                return self.args.converted_output
        else:
            return self.args.input

    @staticmethod
    def delete_dicoms(files):
        print("Deleting dicom files...")
        for file in files:
            os.remove(file)
        print("Finished deleting dicom files.")

    @staticmethod
    def __install_dcm2niix():
        print("Please install the latest version of dcm2niix!")
        print("You can find instructions on how to install it here: https://github.com/rordenlab/dcm2niix")
        print("After installing dcm2niix, rerun the script.")
        print("P.S. If it still doesn't work, you can try to download dcm2niix "
              "binary from here: https://github.com/rordenlab/dcm2niix/releases")
        print("and copy it to the same folder as this script.")
