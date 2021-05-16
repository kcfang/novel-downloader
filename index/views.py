from django.shortcuts import render
from django.conf import settings
from django.http import Http404
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError


import os
import sys
import glob
import json
import subprocess
import threading
from contextlib import contextmanager


@contextmanager
def chdir(d):
    try:
        orig = os.getcwd()
        os.chdir(d)
        yield
    finally:
        os.chdir(orig)


def index(request):
    return render(request, 'index.html')


def get_id(url):
    return url.split("/")[-1]


def get_image(info):
    try:
        image = settings.STATIC_URL + info['images'][0]['path']
    except IndexError:
        image = settings.STATIC_URL + 'full/default_no_thumbnail.jpg'

    return image


def load_info(f):
    with open(f, 'r') as fd:
        j = json.load(fd)

    return {
        'title': j['title'],
        'author': j['author'],
        'id': get_id(j['url']),
        'image': get_image(j)
    }


def get_novels(request, type):
    novels = []
    for f in glob.glob(os.path.join(settings.NOVEL_INFO, '*.json')):
        novels.append(load_info(f))

    return render(request, 'listall.html', {'novels': novels})


def glob_books(d):
    files = [os.path.join(d, f) for f in os.listdir(d)]
    files.sort(key=lambda x: os.path.getmtime(x))
    files = [f.replace(settings.DOWNLOADER_DIR, "") for f in files]
    return files


def get_book(request, id):
    f = os.path.join(settings.NOVEL_INFO, '{}.json'.format(id))
    with open(f, 'r') as fd:
        j = json.load(fd)

    result_dir = j['result_dir']
    d = os.path.join(settings.DOWNLOADER_DIR, result_dir)
    txt = glob_books(os.path.join(d, 'txt'))
    mobi = glob_books(os.path.join(d, 'mobi'))

    book = {
        'title': j['title'],
        'author': j['author'],
        'id': get_id(j['url']),
        'image': get_image(j),
        'chapters': range(0, j['last_index']),
        'txt': txt,
        'mobi': mobi,
    }

    return render(request, 'book.html', {'book': book})


def get_online(request, id, chapter):
    f = os.path.join(settings.NOVEL_DIR, id, chapter + '.json')
    if not os.path.isfile(f):
        return Http404('chapter not found')

    with open(f, 'r') as fd:
        book = json.load(fd)

    book['id'] = id
    book['priv'] = int(chapter)-1
    book['next'] = int(chapter)+1
    return render(request, 'view.html', {'book': book})


def download(request):
    novels = []
    url = request.POST.get('url')
    val = URLValidator()
    try:
        val(url)
    except ValidationError:
        return render(request, 'index.html', {'msg': '輸入錯誤!! 請重新輸入!!'})

    if 'https://czbooks.cc' not in url and 'https://czbooks.net' not in url:
        return render(request, 'index.html', {'msg': '輸入網站並不是屬於 <a href="https://czbooks.xxx">https://czbooks.xxx</a>'})

    with chdir(settings.DOWNLOADER_DIR):
        print(os.getcwd())
        subprocess.check_call(['python', 'run.py', '--url', url])

    info_file = os.path.join(settings.NOVEL_INFO, '{}.json'.format(url.split("/")[-1]))

    return render(request, 'listall.html', {'novels': [load_info(info_file)]})
