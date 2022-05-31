import argparse
import os


# create the top-level parser class
class Parser:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(description='Process a folder of MRI images with subjects')
        self.args = None

        self.parser.add_argument('--input', '-i', help='Input folder (BIDS format or DICOM files)',
                                 required=True, type=os.path.abspath)
        self.parser.add_argument('--converted_output', '-co', help='Output folder for converted files',
                                 default='converted_output')
        self.parser.add_argument('--output', '-o', help='Output folder for processed files '
                                                        '(bids_input/derivatives/pipeline_registration by default)',
                                 default='derivatives/pipeline_registration')

    def parse(self):
        self.args = self.parser.parse_args()
        self.args = self.__improved_arguments()
        return self.args

    def __improved_arguments(self):
        self.args.converted_output = os.path.join(self.args.input, self.args.converted_output)
        self.args.output = os.path.join(self.args.input, self.args.output)
        return self.args

    def get_subjects(self):
        subjects = [name for name in os.listdir(self.args.input) if os.path.isdir(os.path.join(self.args.input, name))]
        try:
            subjects.remove('converted_output')
        except ValueError:
            pass
        try:
            # just to be sure that the converted_output folder is not included in case of error of smth else
            subjects.remove('derivatives/pipeline_registration')
        except ValueError:
            pass
        return subjects

    def __str__(self) -> str:
        if not self.args:
            return self.parser.description
        else:
            outdict = vars(self.args)
            return str(outdict)
