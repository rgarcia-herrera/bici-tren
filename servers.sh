#!/bin/bash

source venv/bin/activate

cd brouter/standalone
./server.sh

#cd ../../abm
#FLASK_APP=viz_server.py flask run
