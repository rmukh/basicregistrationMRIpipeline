from nipype.interfaces.io import BIDSDataGrabber, DataSink
from nipype.pipeline.engine import Node


def data_source(path):
    bg = Node(BIDSDataGrabber(), name='bids_source')
    bg.inputs.base_dir = path
    bg.inputs.output_query = {
        "T1w": {
            "datatype": "anat",
            "suffix": "T1w",
            "extension": ["nii", ".nii.gz"],
        },
        "T2w": {
            "datatype": "anat",
            "suffix": "T2w",
            "extension": ["nii", ".nii.gz"],
        },
        "dwi": {
            "datatype": "dwi",
            "suffix": "dwi",
            "extension": ["nii", ".nii.gz"],
        },
    }
    bg.inputs.raise_on_empty = False
    return bg


def data_sink(out_path):
    ds = Node(DataSink(), name='data_sink')
    ds.inputs.base_directory = out_path
    return ds
