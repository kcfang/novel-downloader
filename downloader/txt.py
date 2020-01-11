import os
import json

from generator import Generator

class TxtGenerator(Generator):
    filetype = "txt"

    def gen_file(self, targets):
        file_path = self.get_file_path(targets)

        text = ""
        for f in targets:
            with open(self.join_path(f), 'r') as fd:
                j = json.load(fd)
            text += '{}\n{}\n\n'.format(j['chapter'], '\n'.join(j["text"]))

        with open(file_path, 'w') as fd:
            fd.write(text)

        print("Generate - {}.".format(file_path))
        return file_path

