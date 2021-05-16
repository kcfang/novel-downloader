#!/bin/bash

cd $(dirname "${BASH_SOURCE[0]}")/downloader

python run.py --all
