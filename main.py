from shared_core.project_parser import Parser
from shared_core.dicom_conversion import DICOM

parser = Parser()
args = parser.parse()

# detect the subjects in the input directory
subjects = parser.get_subjects()
print("Found {} subjects".format(len(subjects)))
print("Subjects: {}".format(subjects))

dicom = DICOM(args, subjects)
out_folder = dicom.run_conversion()
print("Output folder: {}".format(out_folder))
