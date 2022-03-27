# https://www.lfd.uci.edu/~gohlke/pythonlibs/#python-levenshtein
# Downloaded python_Levenshtein-0.12.2-cp39-cp39-win_amd64.whl
# Then: pip install python_Levenshtein-0.12.2-cp39-cp39-win_amd64.whl
import Levenshtein

import os
import re

class FileMatcher:

    def __init__(self, cat_string, filenames_to_be, filenames_current_pool):
        self.cat_string = cat_string
        self.filenames_to_be = filenames_to_be
        self.filenames_current_pool = filenames_current_pool
    
    def select(self):
        filenames_candidates = []
        expand = True
        changed = False
        while True:
            print(f'\n--- {self.cat_string} tracks should be: ---')
            for i in range(0, len(self.filenames_to_be)):
                print(f'({i + 1}) {self.filenames_to_be[i]}')

            print('\n--- Closest matches: ---')
            
            if expand:
                for filename in self.filenames_to_be:
                    filenames_candidates.append(self.take_most_similar_filename(filename))
                expand = False

            for i in range(0, len(filenames_candidates)):
                if i == len(self.filenames_to_be):
                    print('--- ...')
                print(f'({i + 1}) {filenames_candidates[i]}')

            command = input('\nEnter track number to move a track to top; + to add candidates; enter to confirm: ')
            if re.match('\d+', command):
                index = int(command) - 1
                if index > 0 or index < len(filenames_candidates):
                    filenames_candidates = [ filenames_candidates[index] ] + filenames_candidates[:index] + filenames_candidates[index + 1:]
                    changed = True

            elif command == '+':
                expand = True

            elif command == '':
                break

        return [ changed, filenames_candidates[:len(self.filenames_to_be)] ]

    def take_most_similar_filename(self, pattern):
        best_distance = 1000000 # infinite
        best_filename = None
        for filename in self.filenames_current_pool:
            distance = Levenshtein.distance(pattern, filename)
            if distance < best_distance:
                best_distance = distance
                best_filename = filename
        self.filenames_current_pool.remove(best_filename)
        return best_filename

    # def get_most_similar_filenames_x(self, pattern, candidate_count):
    #     best_distance = [ 1000000 ] * candidate_count # infinite per candidate cell
    #     best_filename = [ None    ] * candidate_count
    #     for filename in self.filenames_current_pool:
    #         distance = Levenshtein.distance(pattern, filename)
    #         for i in range(0, candidate_count):
    #             if distance < best_distance[i]:
    #                 best_distance.insert(i, distance)
    #                 best_distance.pop()
    #                 best_filename.insert(i, filename)
    #                 best_filename.pop()
    #                 break
    #     list(filter(lambda a: a != None, best_filename))
    #     return best_filename
