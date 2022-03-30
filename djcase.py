
# https://www.lfd.uci.edu/~gohlke/pythonlibs/#python-levenshtein
# Downloaded python_Levenshtein-0.12.2-cp39-cp39-win_amd64.whl
# Then: pip install python_Levenshtein-0.12.2-cp39-cp39-win_amd64.whl
import Levenshtein

import glob
import os

class DjCase:
    def __init__(self, vinyl_path):
        self.vinyl_path = vinyl_path

    # def get_most_similar_filename(self, pattern):
    #     best_distance = 1000000 # infinite
    #     best_filename = None
    #     for filename in glob.glob(os.path.join(self.vinyl_path, "*.mp3")):
    #         filename = os.path.basename(filename)
    #         distance = Levenshtein.distance(pattern, filename)
    #         if distance < best_distance:
    #             best_distance = distance
    #             best_filename = filename
    #     return best_filename
