def registration_workflow(num_threads=1):
    from nipype.pipeline.engine import Node, Workflow
    from nipype.interfaces.utility import IdentityInterface, Merge
    from nipype.interfaces.ants import Registration, ApplyTransforms

    inputnode = Node(IdentityInterface(fields=["dwi_nifti", "mean_b0", "t1", "t2"]),
                     name="inputnode")

    outputnode = Node(IdentityInterface(fields=["dwi", "t2"]), name="outputnode")

    # Registration
    reg_b0_to_t2 = Node(Registration(metric=["MI", "MI", "MI"],
                                     transforms=["Rigid", "Affine", "SyN"],
                                     metric_weight=[1, 1, 1],
                                     number_of_iterations=[[500, 250, 100], [500, 250, 100],
                                                           [75, 50, 0]],
                                     convergence_threshold=[1.e-6, 1.e-6, 1.e-6],
                                     convergence_window_size=[10] * 3,
                                     shrink_factors=[[4, 2, 1], [4, 2, 1], [2, 2, 1]],
                                     smoothing_sigmas=[[3, 2, 1], [3, 2, 1], [2, 1, 0]],
                                     radius_or_number_of_bins=[32, 32, 4],
                                     transform_parameters=[(0.1,), (0.1,), (0.2, 3, 0)],
                                     sampling_strategy=["Regular", "Regular", "Random"],
                                     sampling_percentage=[0.25, 0.25, 0.4],
                                     use_histogram_matching=[False, False, False],
                                     winsorize_lower_quantile=0.005,
                                     winsorize_upper_quantile=0.995,
                                     num_threads=num_threads,
                                     float=True,
                                     output_transform_prefix="b0ToT2_",
                                     output_warped_image='warped_b0_to_T2.nii.gz',
                                     output_inverse_warped_image='inverse_warped.nii.gz'),
                        name="b0_to_T2")

    # Registration
    reg_t2_to_t1 = Node(Registration(metric=["MI", "MI", "MI"],
                                     transforms=["Rigid", "Affine", "SyN"],
                                     metric_weight=[1, 1, 1],
                                     number_of_iterations=[[1000, 500, 250, 100], [1000, 500, 250, 100],
                                                           [75, 50, 0]],
                                     convergence_threshold=[1.e-6, 1.e-6, 1.e-6],
                                     convergence_window_size=[10] * 3,
                                     shrink_factors=[[8, 4, 2, 1], [8, 4, 2, 1], [2, 2, 1]],
                                     smoothing_sigmas=[[3, 2, 1, 0], [3, 2, 1, 0], [2, 1, 0]],
                                     radius_or_number_of_bins=[32, 32, 4],
                                     transform_parameters=[(0.1,), (0.1,), (0.2, 3, 0)],
                                     sampling_strategy=["Regular", "Regular", "Regular"],
                                     sampling_percentage=[0.25, 0.25, 0.4],
                                     use_histogram_matching=[False, False, False],
                                     winsorize_lower_quantile=0.005,
                                     winsorize_upper_quantile=0.995,
                                     num_threads=num_threads,
                                     float=True,
                                     output_transform_prefix="T2ToT1_",
                                     output_warped_image='warped_t2_to_t1.nii.gz',
                                     output_inverse_warped_image='inverse_warped.nii.gz'),
                        name="T2_to_T1")

    merge_transforms = Node(Merge(2), name="merge_transform_lists")

    apply_transforms = Node(ApplyTransforms(dimension=3,
                                            input_image_type=3,
                                            interpolation="Linear",
                                            float=True,
                                            num_threads=num_threads,
                                            output_image='warped_dwi.nii.gz'),
                            name="apply_transforms")

    wf = Workflow(name="registration")
    wf.connect([
        # FreeSurfer to native space
        (inputnode, reg_b0_to_t2, [("mean_b0", "moving_image")]),
        (inputnode, reg_b0_to_t2, [("t2", "fixed_image")]),

        (inputnode, reg_t2_to_t1, [("t2", "moving_image")]),
        (inputnode, reg_t2_to_t1, [("t1", "fixed_image")]),

        (reg_t2_to_t1, merge_transforms, [("forward_transforms", "in1")]),
        (reg_b0_to_t2, merge_transforms, [("forward_transforms", "in2")]),

        (inputnode, apply_transforms, [("t1", "reference_image")]),
        (inputnode, apply_transforms, [("dwi_nifti", "input_image")]),
        (merge_transforms, apply_transforms, [("out", "transforms")]),

        (apply_transforms, outputnode, [("output_image", "dwi")]),
        (reg_t2_to_t1, outputnode, [("warped_image", "t2")])
    ])

    return wf
