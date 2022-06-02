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
        self.parser.add_argument('--ncpus', '-nc', help='Number of threads to use '
                                                        'for processing (default max available)',
                                 default=os.cpu_count(), type=int)
        self.parser.add_argument('--final_cleanup', '-fc', help='Remove the temp folder after registration',
                                 default=None, type=bool)
        self.parser.add_argument('--debug', '-d', help='Debug mode', action='store_true')

    def parse(self) -> argparse.Namespace:
        self.args = self.parser.parse_args()
        self.args = self._improved_arguments()
        return self.args

    def _improved_arguments(self) -> argparse.Namespace:
        self.args.converted_output = os.path.join(self.args.input, self.args.converted_output)
        self.args.output = os.path.join(self.args.input, self.args.output)
        return self.args

    @staticmethod
    def _try_remove(subj, path) -> None:
        try:
            subj.remove(path)
        except (FileNotFoundError, ValueError):
            pass

    def get_subjects(self) -> list:
        subjects = []
        try:
            subjects = [name for name in os.listdir(self.args.input) if
                        os.path.isdir(os.path.join(self.args.input, name))]
        except FileNotFoundError:
            print("Not a valid input folder!")
            exit(0)

        self._try_remove(subjects, 'converted_output')
        self._try_remove(subjects, 'scrap')
        self._try_remove(subjects, 'derivatives')

        return subjects

    def __str__(self) -> str:
        if not self.args:
            return self.parser.description
        else:
            outdict = vars(self.args)
            return str(outdict)
