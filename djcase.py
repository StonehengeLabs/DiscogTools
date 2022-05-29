import glob
import os

class DjCase:
    def __init__(self, vinyl_path):
        self.vinyl_path = vinyl_path

    def mp3_filepaths(self):
        adjusted = list()
        for path in glob.glob(os.path.join(self.vinyl_path, "*.mp3")):
            adjusted.append(path.replace("\\","/"))
        return adjusted

    def mp3_filenames(self):
        return [os.path.basename(x) for x in self.mp3_filepaths()]
