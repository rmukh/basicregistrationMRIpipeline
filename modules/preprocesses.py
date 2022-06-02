def preprocess_dwi_workflow(num_threads=1):
    from nipype.interfaces.mrtrix3.preprocess import DWIDenoise, MRDeGibbs
    from nipype.interfaces.mrtrix3 import MRConvert, MRMath, DWIBiasCorrect, DWIExtract
    from .mrtrix3_extra_interfaces import Threshold, DWIPreprocCustom
    from nipype.pipeline.engine import Node, Workflow
    from nipype.interfaces.utility import IdentityInterface

    inputnode = Node(IdentityInterface(fields=["dwi", "pe", "rt"]),
                     name="inputnode")
    outputnode = Node(IdentityInterface(fields=["dwi_nifti", "bvec", "bval", "mean_b0"]),
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

    # Extract b0 from DWI and compute mean and convert to nifti
    extract_b0 = Node(DWIExtract(bzero=True, nthreads=num_threads, out_file="b0vols.mif"), name="extract_b0")
    mean_b0 = Node(MRMath(operation="mean", axis=3, nthreads=num_threads, out_file="mean_b0.mif"), name="mean_b0")
    cnvrt_mean_b0 = Node(MRConvert(axes=[0, 1, 2], nthreads=num_threads, out_file="mean_b0.nii.gz"),
                         name="convert_mean_b0")

    # dwi convert to nifti
    cnvrt_dwi = Node(MRConvert(axes=[0, 1, 2, 3], nthreads=num_threads, out_file="dwi.nii.gz"), name="convert_dwi")

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

        (bias, cnvrt_dwi, [("out_file", "in_file")]),

        (bias, extract_b0, [("out_file", "in_file")]),
        (extract_b0, mean_b0, [("out_file", "in_file")]),
        (mean_b0, cnvrt_mean_b0, [("out_file", "in_file")]),

        (eddy, outputnode, [("out_fsl_bval", "bval"),
                            ("out_fsl_bvec", "bvec")]),
        (cnvrt_dwi, outputnode, [("out_file", "dwi_nifti")]),
        (cnvrt_mean_b0, outputnode, [("out_file", "mean_b0")]),
    ])

    return wf


def preprocess_anat_workflow(num_threads=1):
    from nipype.interfaces.ants import DenoiseImage, N4BiasFieldCorrection
    from nipype.pipeline.engine import Node, Workflow
    from nipype.interfaces.utility import IdentityInterface, Function
    from modules.utility_functions import get_single_element

    inputnode = Node(IdentityInterface(fields=["t1", "t2"]), name="inputnode")
    outputnode = Node(IdentityInterface(fields=["t1", "t2"]), name="outputnode")

    clean_path_node_t1 = Node(Function(input_names=["in_path"],
                                       output_names=["out_path"],
                                       function=get_single_element),
                              name="clean_path_node_t1")
    clean_path_node_t2 = Node(Function(input_names=["in_path"],
                                       output_names=["out_path"],
                                       function=get_single_element),
                              name="clean_path_node_t2")

    # non-local means with Rician denoising correction
    denoise_t1 = Node(DenoiseImage(dimension=3, noise_model='Rician', shrink_factor=2,
                                   num_threads=num_threads),
                      name="denoising_t1")
    denoise_t2 = Node(DenoiseImage(dimension=3, noise_model='Rician', shrink_factor=2,
                                   num_threads=num_threads),
                      name="denoising_t2")

    # N4 bias correction
    n4_t1 = Node(N4BiasFieldCorrection(dimension=3, n_iterations=[300, 150, 75, 50],
                                       convergence_threshold=1e-6, num_threads=num_threads),
                 name="n4_t1")
    n4_t2 = Node(N4BiasFieldCorrection(dimension=3, n_iterations=[300, 150, 75, 50],
                                       convergence_threshold=1e-6, num_threads=num_threads),
                 name="n4_t2")

    wf = Workflow(name="PreprocessANAT")
    wf.connect([
        (inputnode, clean_path_node_t1, [("t1", "in_path")]),
        (inputnode, clean_path_node_t2, [("t2", "in_path")]),

        (clean_path_node_t1, denoise_t1, [("out_path", "input_image")]),
        (denoise_t1, n4_t1, [("output_image", "input_image")]),

        (clean_path_node_t2, denoise_t2, [("out_path", "input_image")]),
        (denoise_t2, n4_t2, [("output_image", "input_image")]),

        (n4_t1, outputnode, [("output_image", "t1")]),
        (n4_t2, outputnode, [("output_image", "t2")])
    ])

    return wf
