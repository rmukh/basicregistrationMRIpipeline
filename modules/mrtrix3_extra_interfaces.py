"""
Authored by: Rinat Mukhometzianov
All rights reserved. (C) 2022
"""

from nipype.interfaces.mrtrix3.base import MRTrix3BaseInputSpec, MRTrix3Base
from nipype.interfaces.base import TraitedSpec, traits, CommandLine
from os.path import abspath


class MRCATInputSpec(MRTrix3BaseInputSpec):
    in_files = traits.List(traits.File(exists=True),
                           argstr="%s",
                           position=-2,
                           mandatory=True,
                           desc="input DWI volumes"
                           )

    axis = traits.Int(
        3,
        argstr="-axis %d",
        desc="specified axis to perform the operation along"
    )

    out_file = traits.File(
        argstr="%s",
        position=-1,
        name_template="%s_merged",
        name_source=["in_files"],
        keep_extension=True,
        desc="the merged output",
    )


class MRCATOutputSpec(TraitedSpec):
    out_file = traits.File(desc="the output merged DWI volume", exists=True)


class MRCAT(MRTrix3Base):
    _cmd = "mrcat"
    input_spec = MRCATInputSpec
    output_spec = MRCATOutputSpec


class ThresholdInputSpec(MRTrix3BaseInputSpec):
    in_file = traits.File(exists=True,
                          argstr="%s",
                          position=0,
                          mandatory=True,
                          desc="input DWI volumes"
                          )

    axis = traits.String(
        "",
        position=1,
        argstr="-max %s",
        mandatory=True,
        usedefault=True
    )

    out_file = traits.File(
        argstr="%s",
        position=2,
        name_template="%s_thresholded",
        name_source="in_file",
        keep_extension=True,
        desc="the output negative values removed volume",
    )


class ThresholdOutputSpec(TraitedSpec):
    out_file = traits.File(desc="the output negative values removed volume", exists=True)


class Threshold(CommandLine):
    _cmd = "mrcalc 0"
    input_spec = ThresholdInputSpec
    output_spec = ThresholdOutputSpec


class MaskDilationInputSpec(MRTrix3BaseInputSpec):
    in_file = traits.File(exists=True,
                          argstr="%s",
                          position=0,
                          mandatory=True,
                          desc="input mask"
                          )

    filter = traits.String(
        "dilate",
        position=1,
        argstr="%s",
        mandatory=True,
        usedefault=True
    )

    out_file = traits.File(
        argstr="%s",
        position=2,
        name_template="%s_thresholded",
        name_source="in_file",
        keep_extension=True,
        desc="dilated mask",
    )


class MaskDilationOutputSpec(TraitedSpec):
    out_file = traits.File(desc="dilated mask volume", exists=True)


class MaskDilation(CommandLine):
    _cmd = "maskfilter -npass 4"
    input_spec = MaskDilationInputSpec
    output_spec = MaskDilationOutputSpec


class MaskConnectInputSpec(MRTrix3BaseInputSpec):
    in_file = traits.File(exists=True,
                          argstr="%s",
                          position=0,
                          mandatory=True,
                          desc="input mask"
                          )

    filter = traits.String(
        "connect",
        position=1,
        argstr="%s",
        mandatory=True,
        usedefault=True
    )

    out_file = traits.File(
        argstr="%s",
        position=2,
        name_template="%s_thresholded",
        name_source="in_file",
        keep_extension=True,
        desc="connect mask",
    )


class MaskConnectOutputSpec(TraitedSpec):
    out_file = traits.File(desc="connected mask volume", exists=True)


class MaskConnect(CommandLine):
    _cmd = "maskfilter -largest -connectivity"
    input_spec = MaskDilationInputSpec
    output_spec = MaskDilationOutputSpec


class MaskCleanInputSpec(MRTrix3BaseInputSpec):
    in_file = traits.File(exists=True,
                          argstr="%s",
                          position=0,
                          mandatory=True,
                          desc="input mask"
                          )

    filter = traits.String(
        "clean",
        position=1,
        argstr="%s",
        mandatory=True,
        usedefault=True
    )

    out_file = traits.File(
        argstr="%s",
        position=2,
        name_template="%s_thresholded",
        name_source="in_file",
        keep_extension=True,
        desc="dilated mask",
    )


class MaskCleanOutputSpec(TraitedSpec):
    out_file = traits.File(desc="clean mask volume", exists=True)


class MaskClean(CommandLine):
    _cmd = "maskfilter -scale 4"
    input_spec = MaskDilationInputSpec
    output_spec = MaskDilationOutputSpec


class DivideInputSpec(MRTrix3BaseInputSpec):
    in_file = traits.File(exists=True,
                          argstr="%s",
                          position=0,
                          mandatory=True,
                          desc="input DWI volumes"
                          )

    value = traits.Float(
        "1.0",
        position=1,
        argstr="%f -div",
        mandatory=True
    )

    out_file = traits.File(
        argstr="%s",
        position=2,
        name_template="%s_divided",
        name_source="in_file",
        keep_extension=True,
        desc="the output divided by number",
    )


class DivideOutputSpec(TraitedSpec):
    out_file = traits.File(desc="the divided output volume", exists=True)


class Divide(CommandLine):
    _cmd = "mrcalc"
    input_spec = DivideInputSpec
    output_spec = DivideOutputSpec


class DwinormaliseInputSpec(MRTrix3BaseInputSpec):
    in_file = traits.File(exists=True,
                          argstr="%s",
                          position=0,
                          mandatory=True,
                          desc="input DWI volume"
                          )

    input_mask = traits.File(exists=True,
                             argstr="%s",
                             position=1,
                             mandatory=True,
                             desc="input mask"
                             )

    out_file = traits.File(
        argstr="%s",
        position=2,
        name_template="%s_normalised",
        name_source=["in_file"],
        keep_extension=True,
        desc="normalised output",
    )


class DwinormaliseOutputSpec(TraitedSpec):
    out_file = traits.File(desc="the output normalised DWI volume", exists=True)


class Dwinormalise(MRTrix3Base):
    _cmd = "dwinormalise individual"
    input_spec = DwinormaliseInputSpec
    output_spec = DwinormaliseOutputSpec


def concat_grads(bvec, bval):
    return bvec, bval


class DWIPreprocCustomInputSpec(MRTrix3BaseInputSpec):
    in_file = traits.File(
        exists=True, argstr="%s", position=0, mandatory=True, desc="input DWI image"
    )
    out_file = traits.File(
        "preproc.mif",
        argstr="%s",
        mandatory=True,
        position=1,
        usedefault=True,
        desc="output file after preprocessing",
    )
    rpe_options = traits.Enum(
        "none",
        "pair",
        "all",
        "header",
        argstr="-rpe_%s",
        position=2,
        mandatory=True,
        desc='Specify acquisition phase-encoding design. "none" for no reversed phase-encoding image, '
             '"all" for all DWIs have opposing phase-encoding acquisition, '
             '"pair" for using a pair of b0 volumes for inhomogeneity field estimation only, '
             'and "header" for phase-encoding information can be found in the image header(s)',
    )
    pe_dir = traits.Str(
        argstr="-pe_dir %s",
        mandatory=True,
        desc="Specify the phase encoding direction of the input series, can be a signed axis number (e.g. -0, 1, +2),"
             " an axis designator (e.g. RL, PA, IS), or NIfTI axis codes (e.g. i-, j, k)",
    )
    ro_time = traits.Float(
        argstr="-readout_time %f",
        desc="Total readout time of input series (in seconds)",
    )
    in_epi = traits.File(
        exists=True,
        argstr="-se_epi %s",
        desc="Provide an additional image series consisting of spin-echo EPI images, which is to be used "
             "exclusively by topup for estimating the inhomogeneity field (i.e. it will not form part of "
             "the output image series)",
    )
    align_seepi = traits.Bool(
        argstr="-align_seepi",
        desc="Achieve alignment between the SE-EPI images used for inhomogeneity field estimation, and the DWIs",
    )
    eddy_options = traits.Str(
        argstr='-eddy_options "%s"',
        desc="Manually provide additional command-line options to the eddy command",
    )
    topup_options = traits.Str(
        argstr='-topup_options "%s"',
        desc="Manually provide additional command-line options to the topup command",
    )
    export_grad_mrtrix = traits.Bool(
        argstr="-export_grad_mrtrix", desc="export new gradient files in mrtrix format"
    )
    export_grad_fsl = traits.Bool(
        argstr="-export_grad_fsl", position=-2, desc="export gradient files in FSL format"
    )
    out_grad_fsl = traits.Tuple(
        traits.File("grad.bvecs", usedefault=True, desc="bvecs"),
        traits.File("grad.bvals", usedefault=True, desc="bvals"),
        argstr="%s %s",
        position=-1,
        usedefault=True,
        requires=["export_grad_fsl"],
        desc="Output (bvecs, bvals) gradients FSL format",
    )


class DWIPreprocCustomOutputSpec(TraitedSpec):
    out_file = traits.File(argstr="%s", desc="output preprocessed image series")
    out_fsl_bvec = traits.File(
        "grad.bvecs",
        argstr="%s",
        usedefault=True,
        desc="exported fsl gradient bvec file",
    )
    out_fsl_bval = traits.File(
        "grad.bvals",
        argstr="%s",
        usedefault=True,
        desc="exported fsl gradient bval file",
    )


class DWIPreprocCustom(MRTrix3Base):
    """
    Perform diffusion image pre-processing using FSL's eddy tool;
     including inhomogeneity distortion correction using FSL's topup tool if possible
    """

    _cmd = "dwifslpreproc"
    input_spec = DWIPreprocCustomInputSpec
    output_spec = DWIPreprocCustomOutputSpec

    def _list_outputs(self):
        outputs = self.output_spec().get()
        outputs["out_file"] = abspath(self.inputs.out_file)

        if self.inputs.export_grad_fsl:
            outputs["out_fsl_bvec"] = abspath(self.inputs.out_grad_fsl[0])
            outputs["out_fsl_bval"] = abspath(self.inputs.out_grad_fsl[1])

        return outputs
