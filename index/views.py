from django.shortcuts import render
from django.http import StreamingHttpResponse
from django.conf import settings
from django.template import loader, Context, Template
from django.http import StreamingHttpResponse
from django.views.decorators.http import condition
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

def load_info(f):
    with open(f, 'r') as fd:
        j = json.load(fd)

    return {
        'title': j['title'],
        'author': j['author'],
        'id': get_id(j['url']),
        'image': settings.STATIC_URL + j['images'][0]['path']
    }


def get_novels(request, type):
    novels = []
    for f in glob.glob(os.path.join(settings.NOVEL_INFO, '*.json')):
        novels.append(load_info(f))

    return render(request, 'listall.html', {'novels': novels})


def get_book(request, id):
    f = os.path.join(settings.NOVEL_INFO, '{}.json'.format(id))
    with open(f, 'r') as fd:
        j = json.load(fd)

    result_dir = j['result_dir']
    txt = sorted(glob.glob(os.path.join(settings.DOWNLOADER_DIR, result_dir, 'txt', '*')))
    txt = [f.replace(settings.DOWNLOADER_DIR, "") for f in txt]
    mobi = sorted(glob.glob(os.path.join(settings.DOWNLOADER_DIR, result_dir, 'mobi', '*')))
    mobi = [f.replace(settings.DOWNLOADER_DIR, "") for f in mobi]

    book = {
        'title': j['title'],
        'author': j['author'],
        'id': get_id(j['url']),
        'image': settings.STATIC_URL + j['images'][0]['path'],
        'txt': txt,
        'mobi': mobi,
    }

    return render(request, 'book.html', {'book': book})


def download(request):
    novels = []
    url = request.POST.get('url')
    val = URLValidator()
    print(url)
    try:
        val(url)
    except ValidationError:
        return render(request, 'index.html', {'msg': '輸入錯誤!! 請重新輸入!!'})

    if 'https://czbooks.net' not in url:
        return render(request, 'index.html', {'msg': '輸入網站並不是屬於 <a href="https://czbooks.net">https://czbooks.net</a>'})

    with chdir(settings.DOWNLOADER_DIR):
        print(os.getcwd())
        subprocess.check_call(['python', 'run.py', '--url', url])

    info_file = os.path.join(settings.NOVEL_INFO, '{}.json'.format(url.split("/")[-1]))

    return render(request, 'listall.html', {'novels': [load_info(info_file)]})
