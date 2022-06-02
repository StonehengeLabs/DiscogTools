# https://www.lfd.uci.edu/~gohlke/pythonlibs/#python-levenshtein
# Downloaded python_Levenshtein-0.12.2-cp39-cp39-win_amd64.whl
# Then: pip install python_Levenshtein-0.12.2-cp39-cp39-win_amd64.whl
import Levenshtein

import os
import re
import glob
import webbrowser

class FileMatcher:

    def __init__(self, release_id, cat_string, filenames_to_be, glob_path, glob_pattern):
        self.release_id = release_id
        self.cat_string = cat_string
        self.filenames_to_be = filenames_to_be
        self.glob_path = glob_path
        self.glob_pattern = glob_pattern

    def select(self):
        filenames_candidates = []
        expand = True
        renamed = False
        filenames_current_pool = self.rescan()
        while True:
            print(f'\n--- {self.cat_string} files to be: ---')
            for i in range(0, len(self.filenames_to_be)):
                print(f'({i + 1}) {self.filenames_to_be[i]}')

            print('\n--- To be built from: ---')
            
            if expand:
                for filename in self.filenames_to_be:
                    filenames_candidates.append(self.take_most_similar_filename(filename, filenames_current_pool))
                expand = False

            for i in range(0, len(filenames_candidates)):
                if i == len(self.filenames_to_be):
                    print('--- ...')
                size = int(os.path.getsize(os.path.join(self.glob_path, filenames_candidates[i])) / 1024 / 1024)
                print(f'({i + 1}) {filenames_candidates[i]} ({size}MB)')

            command = input('\nEnter track number to move a track to top; + to add candidates; r to rescan; b to browse; enter to confirm: ')
            if re.match('\d+', command):
                index = int(command) - 1
                if index > 0 or index < len(filenames_candidates):
                    filenames_candidates = [ filenames_candidates[index] ] + filenames_candidates[:index] + filenames_candidates[index + 1:]
                    renamed = True

            elif command == '+':
                expand = True

            elif command == 'r':
                filenames_current_pool = self.rescan()
                filenames_candidates = []
                expand = True

            elif command == 'b':
                webbrowser.open(f'https://www.discogs.com/release/{self.release_id}', new=0, autoraise=True)

            elif command == '':
                break

        return [ renamed, filenames_candidates[:len(self.filenames_to_be)] ]

    def rescan(self):
        return [os.path.basename(x) for x in glob.glob(os.path.join(self.glob_path, self.glob_pattern))]

    def take_most_similar_filename(self, pattern, pool):
        best_filename = FileMatcher.get_most_similar_filename(pattern, pool)
        pool.remove(best_filename)
        return best_filename

    @staticmethod
    def get_most_similar_filename(pattern, pool):
        best_distance = 1000000 # infinite
        best_filename = None
        for filename in pool:
            distance = Levenshtein.distance(pattern, filename)
            if distance < best_distance:
                best_distance = distance
                best_filename = filename
        return best_filename
