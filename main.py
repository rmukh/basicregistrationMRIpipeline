import datetime
import os.path as op
import shutil

from nipype.pipeline.engine import Workflow

from shared_core.project_parser import Parser
from shared_core.dicom_conversion import DICOM
from shared_core.bids_checks import BIDS

from modules.data_handler import data_source, bids_grabber, data_sink, mif_input_combiner, get_meta_parameters
from modules.preprocesses import preprocess_dwi_workflow, preprocess_anat_workflow
from modules.registration import registration_workflow

now = datetime.datetime.now()

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
    print("BIDS compliant dataset!")
subjects = bids.get_bids_subjects()

out_folder = bids.get_work_dir()
scrap_directory = op.join(out_folder, "scrap")

# IO
source_iterator = data_source(subjects)
bids_source = bids_grabber(out_folder)
sink = data_sink(out_folder, args.output)

# main processing modules (workflows)
combine_dwi = mif_input_combiner(args.ncpus)
combine_dwi.base_dir = scrap_directory

meta_parameters = get_meta_parameters()
preprocess_dwi = preprocess_dwi_workflow(args.ncpus)
preprocess_anat = preprocess_anat_workflow(args.ncpus)
registration = registration_workflow(args.ncpus)

print(f"Starting workflow with {args.ncpus} threads")
wf = Workflow(name="pipeline_registration", base_dir=scrap_directory)
if args.debug:
    wf.config['execution'] = {'stop_on_first_crash': 'True'}

wf.connect([
    (source_iterator, bids_source, [("subject", "subject")]),
    (bids_source, combine_dwi, [("dwi", "inputnode.dwi"),
                                ("bvec", "inputnode.bvec"),
                                ("bval", "inputnode.bval")]),
    (bids_source, meta_parameters, [("dwi_meta", "meta_path")]),
    (combine_dwi, preprocess_dwi, [("outputnode.dwi", "inputnode.dwi")]),
    (meta_parameters, preprocess_dwi, [("pe", "inputnode.pe"),
                                       ("rt", "inputnode.rt")]),
    (bids_source, preprocess_anat, [("T1w", "inputnode.t1"),
                                    ("T2w", "inputnode.t2")]),

    (preprocess_dwi, registration, [("outputnode.mean_b0", "inputnode.mean_b0"),
                                    ("outputnode.dwi_nifti", "inputnode.dwi_nifti")]),
    (preprocess_anat, registration, [("outputnode.t1", "inputnode.t1"),
                                     ("outputnode.t2", "inputnode.t2")]),
    
    (preprocess_anat, sink, [("outputnode.t1", "dwi.@t1")]),
    (registration, sink, [("outputnode.dwi", "dwi.@dwi"),
                          ("outputnode.t2", "anat.@t2")]),
    (preprocess_dwi, sink, [("outputnode.bvec", "dwi.@dwi_bvec"),
                            ("outputnode.bval", "dwi.@dwi_bval")])
])

# Run
wf.run()

print("Total time: ", str(datetime.datetime.now() - now))
if not args.final_cleanup:
    yn = input("Do you want to delete the temporary directory? [y/n] ")
    if yn.lower() == "y":
        args.final_cleanup = True
    else:
        args.final_cleanup = False

if args.final_cleanup:
    print("Deleting temporary directory")
    shutil.rmtree(scrap_directory)
