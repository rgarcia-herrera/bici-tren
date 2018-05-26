#!/bin/bash

source ../venv/bin/activate

python rides_sim.py --log $1 --N 160 --steps 10 --threads 8
