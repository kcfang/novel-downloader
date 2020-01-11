import os
import glob

from crawler import settings


def get_url_id(url):
    if url.endswith('/'):
        u = url.split('/')[-2]
    else:
        u = url.split('/')[-1]
    return u


def get_status_file(url):
    os.makedirs(settings.NOVEL_STATUS, exist_ok=True)
    return os.path.join(settings.NOVEL_STATUS, get_url_id(url) + '.json')


def get_novel_dir(url):
    d = os.path.join(settings.NOVEL_WORKDIR, get_url_id(url))
    os.makedirs(d, exist_ok=True)
    return d

def get_novel_prefix(title, author):
    return '{} {}'.format(title, author)


def get_result_dir(title, author):
    return os.path.join(settings.NOVEL_RESULT, get_novel_prefix(title, author))
