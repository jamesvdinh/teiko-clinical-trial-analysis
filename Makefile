.PHONY: setup pipeline dashboard

setup:
	pip install -r requirements.txt

pipeline:
	python3 scripts/load_data.py
	python3 scripts/run_analysis.py

dashboard:
	streamlit run app.py
