#!/usr/bin/env bash
cd "$(dirname "$0")"
echo "Creating virtual environment..."
python3 -m venv .venv
source .venv/bin/activate
pip install ttkbootstrap
echo ""
echo "Done. Run with: ./run.sh"
