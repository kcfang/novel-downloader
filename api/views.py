# -*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import JsonResponse
import sys
import os
import subprocess
Root = os.path.dirname(__file__)
sys.path.append(Root + "/tools")
import get_novel

MaxConnect = 5
# Create your views here.

class Logger(object):
    def __init__(self, filename="Default.log"):
        self.terminal = sys.stdout
        self.log = open(filename, "a", 0)

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

def connection_limit():
    return len(os.listdir("log/")) >= MaxConnect

def genMobi(request):
    if "url" not in request.GET:
        return JsonResponse({"fail_msg": "url not found"})

    if connection_limit():
        return JsonResponse({"fail_msg": "Server can only serve %s connections at once. Please wait" % MaxConnect})

    url = request.GET['url']
    page = 30
    if "page" in request.GET:
        page = request.GET['page']

    id = request.GET['id']
    log = "log/" + id
    sys.stdout = Logger(log)
    result = get_novel.get_novel(url, Root + "/static", int(page))
    os.remove(log)
    mobi = [u.replace(Root, "") for u in result]

    return JsonResponse({"mobi": mobi})

def getlog(request):
    id = request.GET['id']
    if not os.path.isfile("log/" + id):
        return JsonResponse({"success": True})

    log = subprocess.check_output(["cat", "log/" + id]).split("\n")

    return JsonResponse({"log": log})
