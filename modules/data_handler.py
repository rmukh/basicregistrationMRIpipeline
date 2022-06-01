import os.path

from nipype.interfaces.io import BIDSDataGrabber, DataSink
from nipype.pipeline.engine import Node, Workflow
from nipype.interfaces.utility import IdentityInterface
from nipype.interfaces.mrtrix3 import MRConvert
from .mrtrix3_extra_interfaces import MRCAT


def data_source(path):
    bg = Node(BIDSDataGrabber(), name='bids_source')
    bg.inputs.base_dir = path
    bg.inputs.output_query = {
        "T1w": {
            "datatype": "anat",
            "suffix": "T1w",
            "extension": ["nii", "nii.gz"],
        },
        "T1_meta": {
            "datatype": "anat",
            "suffix": "T1w",
            "extension": [".json"],
        },
        "T2w": {
            "datatype": "anat",
            "suffix": "T2w",
            "extension": ["nii", "nii.gz"],
        },
        "T2_meta": {
            "datatype": "anat",
            "suffix": "T2w",
            "extension": [".json"],
        },
        "dwi": {
            "datatype": "dwi",
            "suffix": "dwi",
            "extension": ["nii", "nii.gz"],
        },
        "dwi_meta": {
            "datatype": "dwi",
            "suffix": "dwi",
            "extension": [".json"],
        },
        "bvec": {
            "datatype": "dwi",
            "suffix": "dwi",
            "extension": ["bvec"],
        },
        "bval": {
            "datatype": "dwi",
            "suffix": "dwi",
            "extension": ["bval"],
        },
    }
    bg.inputs.raise_on_empty = False
    return bg


def data_sink(out_path, subfolder, bids_subjects):
    out = os.path.join(out_path, subfolder)
    ds = Node(DataSink(), name='data_sink')
    ds.inputs.base_directory = out
    ds.iterables = ('subject', bids_subjects)
    return ds


def mif_input_combiner(num_threads=1):
    inputnode = Node(IdentityInterface(fields=["files_in", "bvec_in", "bval_in"]), name="inputnode")
    outputnode = Node(IdentityInterface(fields=["dwi_out"]), name="outputnode")

    merge = Node(MRCAT(nthreads=num_threads), name="merger")
    make_mif = Node(MRConvert(nthreads=num_threads), name="combined_mif_creator")

    wf = Workflow(name="MIF_combiner")
    wf.connect([
        (inputnode, merge, [("files_in", "in_files")]),

        (merge, make_mif, [("out_file", "in_file")]),
        (inputnode, make_mif, [("bvec_in", "in_bvec"),
                               ("bval_in", "in_bval")]),

        (make_mif, outputnode, [("out_file", "dwi_out")]),
    ])

    return wf
