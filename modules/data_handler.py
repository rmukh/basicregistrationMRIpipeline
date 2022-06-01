import os.path

from nipype.interfaces.io import BIDSDataGrabber, DataSink
from nipype.pipeline.engine import Node, Workflow
from nipype.interfaces.utility import IdentityInterface, Function
from nipype.interfaces.mrtrix3 import MRConvert

from .utility_functions import get_single_element


def bids_grabber(path):
    bg = BIDSDataGrabber()
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
    bg.inputs.unpack_single = True
    bg_node = Node(bg, name="bids_grabber")
    return bg_node


def data_source(bids_subjects):
    iterator_node = Node(IdentityInterface(fields=["subject"]),
                         name="subject_iterator")
    iterator_node.iterables = ("subject", bids_subjects)
    iterator_node.inputs.subject = bids_subjects
    return iterator_node


def data_sink(out_path, subfolder):
    out = os.path.join(out_path, subfolder)
    ds = Node(DataSink(), name='data_sink')
    ds.inputs.base_directory = out
    return ds


def extract_pe_rt(meta_path):
    from nipype.interfaces.io import JSONFileGrabber
    from modules.utility_functions import get_single_element

    meta_path = get_single_element(meta_path)
    print("Meta path: {}".format(meta_path))
    jsonSource = JSONFileGrabber()
    jsonSource.inputs.in_file = meta_path

    # extract needed attributes from json file, phase encoding direction, and total readout time
    res = (jsonSource.run()).outputs.get()
    if "PhaseEncodingDirection" in res:
        phase_encoding_direction = res['PhaseEncodingDirection']
    else:
        phase_encoding_direction = "j"

    if "TotalReadoutTime" in res:
        total_readout_time = res['TotalReadoutTime']
    else:
        total_readout_time = 0.145
    return phase_encoding_direction, total_readout_time


def get_meta_parameters():
    get_meta = Node(Function(input_names=["meta_path"],
                             output_names=["pe", "rt"],
                             function=extract_pe_rt), name="meta_parameters")
    return get_meta


def mif_input_combiner(num_threads=1):
    inputnode = Node(IdentityInterface(fields=["dwi", "bvec", "bval"]), name="inputnode")
    outputnode = Node(IdentityInterface(fields=["dwi"]), name="outputnode")

    clean_path_node_dwi = Node(Function(input_names=["in_path"],
                                        output_names=["out_path"],
                                        function=get_single_element),
                               name="clean_path_node_dwi")
    clean_path_node_bvec = Node(Function(input_names=["in_path"],
                                         output_names=["out_path"],
                                         function=get_single_element),
                                name="clean_path_node_bvec")
    clean_path_node_bval = Node(Function(input_names=["in_path"],
                                         output_names=["out_path"],
                                         function=get_single_element),
                                name="clean_path_node_bval")

    make_mif = Node(MRConvert(nthreads=num_threads), name="combined_mif_creator")

    wf = Workflow(name="MIF_combiner")
    wf.connect([
        (inputnode, clean_path_node_dwi, [("dwi", "in_path")]),
        (inputnode, clean_path_node_bvec, [("bvec", "in_path")]),
        (inputnode, clean_path_node_bval, [("bval", "in_path")]),

        (clean_path_node_dwi, make_mif, [("out_path", "in_file")]),
        (clean_path_node_bvec, make_mif, [("out_path", "in_bvec")]),
        (clean_path_node_bval, make_mif, [("out_path", "in_bval")]),

        (make_mif, outputnode, [("out_file", "dwi")]),
    ])

    return wf
