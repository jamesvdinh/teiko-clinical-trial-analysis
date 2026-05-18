#!/bin/bash
set -e

pip install -r requirements.txt
python3 scripts/load_data.py
python3 scripts/run_analysis.py
streamlit run app.py
