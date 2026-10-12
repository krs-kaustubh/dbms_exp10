#!/bin/bash
cd "$(dirname "$0")"
echo "Starting SAMs MySQL Portal on http://localhost:5000 ..."
./venv/bin/python app.py
