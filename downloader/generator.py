import os
import json

from crawler import settings
from crawler.common import get_result_dir, get_novel_prefix

class Generator:
    filetype = ""

    def __init__(self, info):
        self.info = info
        self.novel_dir = info['novel_dir']

    def join_path(self, f):
        return os.path.join(self.novel_dir, f)

    def get_index(self, f):
        return int(f.split('.')[0])

    def get_file_path(self, targets):
        fn = os.path.join(
            get_result_dir(self.info['title'], self.info['author']),
            self.filetype,
            '{} {}-{}.{}'.format(
                get_novel_prefix(self.info['title'], self.info['author']),
                self.get_index(targets[0]),
                self.get_index(targets[-1]),
                self.filetype
            )
        )
        os.makedirs(os.path.dirname(fn), exist_ok=True)
        return fn

    def process(self, files):
        last_file = ""

        while len(files) > settings.NOVEL_MAX_CHAPTER:
            targets = files[:settings.NOVEL_MAX_CHAPTER]
            files = files[settings.NOVEL_MAX_CHAPTER:]

            file_path = self.get_file_path(targets)
            if os.path.isfile(file_path):
                print("SKIP - {} has been generated.".format(file_path))
                continue

            last_file = self.gen_file(targets)

        if files:
            last_file = self.gen_file(files)

        return last_file

    def gen_file(self, targets):
        raise NotImplementedError("gen_file was not implemented")
