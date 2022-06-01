import datetime
import os.path as op
from nipype.pipeline.engine import Workflow

from shared_core.project_parser import Parser
from shared_core.dicom_conversion import DICOM
from shared_core.bids_checks import BIDS

from modules.data_handler import data_source, bids_grabber, data_sink, mif_input_combiner, get_meta_parameters
from modules.preprocesses import preprocess_dwi_workflow

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

preprocess_dwi = preprocess_dwi_workflow(args.ncpus)
meta_parameters = get_meta_parameters()
# dwi_noise = DenoiseDWI(32)
# dwi_noise.base_dir = path_to_results
# unringing = UnringingDWI(32)
# unringing.base_dir = path_to_results
# eddy = EddyCorr(32)
# eddy.base_dir = path_to_results
# bias = BiasCorr(32)
# bias.base_dir = path_to_results
# final_dwi_mask = BrainMask(32)
# final_dwi_mask.base_dir = path_to_results
# t2_mask = T2Mask(32)
# t2_mask.base_dir = path_to_results
# labls = FSlabels(32)
# labls.base_dir = path_to_results
# final_merge = FinalMerge()
# final_merge.base_dir = path_to_results
#

print(f"Starting workflow with {args.ncpus} threads")
wf = Workflow(name="adni", base_dir=scrap_directory)
if args.debug:
    wf.config['execution'] = {'stop_on_first_crash': 'True'}

wf.connect([
    (source_iterator, bids_source, [("subject", "subject")]),
    (bids_source, combine_dwi, [("dwi", "inputnode.dwi"),
                                ("bvec", "inputnode.bvec"),
                                ("bval", "inputnode.bval")]),
    (bids_source, meta_parameters, [("dwi_meta", "meta_path")])
])

# Run
wf.run()

print("Total time: ", str(datetime.datetime.now() - now))
