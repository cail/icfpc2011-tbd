#!/bin/sh

export LD_LIBRARY_PATH=./bin/gcc-4.5.2/debug:$LD_LIBRARY_PATH
export PYTHONPATH=bin/gcc-4.5.2/debug

python test.py

