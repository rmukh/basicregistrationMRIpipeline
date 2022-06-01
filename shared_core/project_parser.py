import argparse
import os


# create the top-level parser class
class Parser:
    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(description='Process a folder of MRI images with subjects')
        self.args = None

        self.parser.add_argument('--input', '-i', help='Root input folder (BIDS format or DICOM files)',
                                 required=True, type=os.path.abspath)
        self.parser.add_argument('--converted_output', '-co', help='Output folder for converted files',
                                 default='converted_output')
        self.parser.add_argument('--output', '-o', help='Output subfolder for the processed data'
                                                        '(<input>/derivatives/pipeline_registration by default)',
                                 default=os.path.join('derivatives', 'pipeline_registration'))
        self.parser.add_argument('--debug', '-d', help='Debug mode', action='store_true')

    def parse(self):
        self.args = self.parser.parse_args()
        self.args = self._improved_arguments()
        return self.args

    def _improved_arguments(self):
        self.args.converted_output = os.path.join(self.args.input, self.args.converted_output)
        self.args.output = os.path.join(self.args.input, self.args.output)
        return self.args

    def get_subjects(self):
        subjects = []
        try:
            subjects = [name for name in os.listdir(self.args.input) if
                        os.path.isdir(os.path.join(self.args.input, name))]
        except FileNotFoundError:
            print("Not a valid input folder!")
            exit(0)

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
