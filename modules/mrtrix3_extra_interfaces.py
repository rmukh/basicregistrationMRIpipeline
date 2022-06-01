"""
Authored by: Rinat Mukhometzianov
All rights reserved. (C) 2022
"""

from nipype.interfaces.mrtrix3.base import MRTrix3BaseInputSpec, MRTrix3Base
from nipype.interfaces.base import TraitedSpec, traits, CommandLine


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
