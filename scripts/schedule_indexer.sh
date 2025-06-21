#!/bin/bash

# Navigate to the project root directory
cd /Users/frisowempe/Desktop/isa_workspace

# Activate the virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# Run the Python indexer script
python isa/indexing/run_indexer.py

# Deactivate the virtual environment if it was activated
if [ -d ".venv" ]; then
    deactivate
fi