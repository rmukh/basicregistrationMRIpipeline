def preprocess_dwi_workflow(num_threads=1):
    from nipype.interfaces.mrtrix3.preprocess import DWIDenoise, MRDeGibbs
    from nipype.interfaces.mrtrix3 import MRConvert, MRMath, DWIBiasCorrect, DWIExtract
    from .mrtrix3_extra_interfaces import Threshold, DWIPreprocCustom
    from nipype.pipeline.engine import Node, Workflow
    from nipype.interfaces.utility import IdentityInterface

    inputnode = Node(IdentityInterface(fields=["dwi", "pe", "rt"]),
                     name="inputnode")
    outputnode = Node(IdentityInterface(fields=["dwi_nifti", "bvec", "bval", "b0s", "mean_b0"]),
                      name="outputnode")

    clipper1 = Node(Threshold(nthreads=num_threads), name="zero_clipper_denoising")
    clipper2 = Node(Threshold(nthreads=num_threads), name="zero_clipper_degibbs")

    # PCA denoising
    denoise = Node(DWIDenoise(nthreads=num_threads), name="denoising")

    # Gibbs ringing removal
    unringing = Node(MRDeGibbs(nthreads=num_threads), name="unringing")

    # Eddy current correction and motion correction
    eddy = Node(DWIPreprocCustom(rpe_options="none",
                                 export_grad_fsl=True,
                                 nthreads=num_threads),
                name="EddyCorrect")

    # B1 field inhomogeneity correction
    bias = Node(DWIBiasCorrect(use_ants=True, nthreads=num_threads),
                name="BiasCorr")

    # extract nifti volumes
    extract_dwi = Node(DWIExtract(nobzero=True, nthreads=num_threads, out_file="dwi_vols.mif"), name="extract_dwi")

    # Extract b0 from DWI and compute mean and convert to nifti
    extract_b0 = Node(DWIExtract(bzero=True, nthreads=num_threads, out_file="b0vols.mif"), name="extract_b0")
    mean_b0 = Node(MRMath(operation="mean", axis=3, nthreads=num_threads, out_file="mean_b0.mif"), name="mean_b0")
    cnvrt_mean_b0 = Node(MRConvert(axes=[0, 1, 2], nthreads=num_threads, out_file="mean_b0.nii.gz"),
                         name="convert_mean_b0")

    # extract dwi and convert to nifti
    cnvrt_dwi = Node(MRConvert(axes=[0, 1, 2, 3], nthreads=num_threads, out_file="dwi.nii.gz"), name="convert_dwi")
    cnvrt_b0 = Node(MRConvert(axes=[0, 1, 2, 3], nthreads=num_threads, out_file="b0s.nii.gz"),
                    name="convert_b0s")

    wf = Workflow(name="PreprocessDWI")
    wf.connect([
        (inputnode, denoise, [("dwi", "in_file")]),
        (denoise, clipper1, [("out_file", "in_file")]),

        (clipper1, unringing, [("out_file", "in_file")]),
        (unringing, clipper2, [("out_file", "in_file")]),

        (inputnode, eddy, [("pe", "pe_dir"),
                           ("rt", "ro_time")]),
        (clipper2, eddy, [("out_file", "in_file")]),

        (eddy, bias, [("out_file", "in_file")]),

        (bias, extract_dwi, [("out_file", "in_file")]),
        (extract_dwi, cnvrt_dwi, [("out_file", "in_file")]),

        (bias, extract_b0, [("out_file", "in_file")]),
        (extract_b0, cnvrt_b0, [("out_file", "in_file")]),
        (extract_b0, mean_b0, [("out_file", "in_file")]),
        (mean_b0, cnvrt_mean_b0, [("out_file", "in_file")]),

        (eddy, outputnode, [("out_fsl_bval", "bval"),
                            ("out_fsl_bvec", "bvec")]),
        (cnvrt_dwi, outputnode, [("out_file", "dwi_nifti")]),
        (cnvrt_b0, outputnode, [("out_file", "b0s")]),
        (cnvrt_mean_b0, outputnode, [("out_file", "mean_b0")]),
    ])

    return wf
