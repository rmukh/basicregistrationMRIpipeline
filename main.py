from shared_core.project_parser import Parser
from shared_core.dicom_conversion import DICOM
from shared_core.bids_checks import BIDS
from nipype.interfaces.io import BIDSDataGrabber

parser = Parser()
args = parser.parse()

# detect the subjects in the input directory
subjects = parser.get_subjects()
print("Found {} subjects".format(len(subjects)))
print("Subjects: {}".format(subjects))

dicom = DICOM(args, subjects)
out_folder = dicom.run_conversion()

bids = BIDS(out_folder, subjects)
bids.run_check()
if bids.is_bids():
    print("BIDS compliant!")

# bg = BIDSDataGrabber()
# bg.inputs.base_dir = test_path
# bg.inputs.output_query = {
#     "T1w": {
#         "datatype": "anat",
#         "suffix": "T1w",
#         "extension": ["nii", ".nii.gz"],
#     },
#     "T2w": {
#         "datatype": "anat",
#         "suffix": "T2w",
#         "extension": ["nii", ".nii.gz"],
#     },
#     "dwi": {
#         "datatype": "dwi",
#         "suffix": "dwi",
#         "extension": ["nii", ".nii.gz"],
#     },
# }
# bg.inputs.raise_on_empty = False
# results = bg.run()
