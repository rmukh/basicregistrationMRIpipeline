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
        self.parser.add_argument('--output', '-o', help='Output folder for processed files',
                                 default='output')

    def parse(self):
        self.args = self.parser.parse_args()
        return self.__improved_arguments()

    def __improved_arguments(self):
        self.args.converted_output = os.path.join(self.args.input, self.args.converted_output)
        self.args.output = os.path.join(self.args.input, self.args.output)
        return self.args

    def __str__(self) -> str:
        if not self.args:
            return self.parser.description
        else:
            outdict = vars(self.args)
            return str(outdict)
