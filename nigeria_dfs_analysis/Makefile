# Nigeria DFS Market Analysis — Makefile
# Run  `make help`  to see all available commands.

.PHONY: help env install data notebooks test lint clean dashboard report zip

PYTHON = python
PIP    = pip
NB     = jupyter nbconvert --to notebook --execute --inplace

help:
	@echo ""
	@echo "Nigeria Digital Financial Services Market Analysis"
	@echo "=================================================="
	@echo ""
	@echo "  make env         Create conda environment from environment.yml"
	@echo "  make install     Install Python dependencies via pip"
	@echo "  make data        Download all public datasets"
	@echo "  make notebooks   Execute all notebooks in order"
	@echo "  make test        Run the test suite"
	@echo "  make lint        Run code quality checks (black, flake8, isort)"
	@echo "  make dashboard   Launch the Streamlit dashboard"
	@echo "  make report      Generate the HTML report from notebooks"
	@echo "  make clean       Remove generated artefacts (keeps raw data)"
	@echo "  make zip         Package the project as a ZIP archive"
	@echo ""

env:
	conda env create -f environment.yml
	@echo "Activate with: conda activate nigeria-dfs"

install:
	$(PIP) install -r requirements.txt
	$(PIP) install -e .

data:
	$(PYTHON) scripts/download_data.py

notebooks:
	@echo "Executing notebooks in order..."
	$(NB) notebooks/00_project_overview_and_business_question.ipynb
	$(NB) notebooks/01_dataset_selection_and_access.ipynb
	$(NB) notebooks/02_data_loading_and_first_inspection.ipynb
	$(NB) notebooks/03_data_quality_checks.ipynb
	$(NB) notebooks/04_data_cleaning_and_feature_engineering.ipynb
	$(NB) notebooks/05_exploratory_analysis.ipynb
	$(NB) notebooks/06_market_sizing_tam_sam_som.ipynb
	$(NB) notebooks/07_competitive_landscape.ipynb
	$(NB) notebooks/08_financial_modelling_and_valuation.ipynb
	$(NB) notebooks/09_risk_assessment_framework.ipynb
	$(NB) notebooks/10_statistical_inference.ipynb
	$(NB) notebooks/11_robustness_checks.ipynb
	$(NB) notebooks/12_publication_figures_and_tables.ipynb
	$(NB) notebooks/13_limitations_and_next_steps.ipynb
	@echo "All notebooks executed successfully."

test:
	pytest tests/ -v --cov=src --cov-report=term-missing

lint:
	black src/ scripts/ tests/ --check
	isort src/ scripts/ tests/ --check-only
	flake8 src/ scripts/ tests/ --max-line-length=88

dashboard:
	streamlit run dashboard/app.py

report:
	jupyter nbconvert --to html notebooks/*.ipynb --output-dir reports/

clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name ".coverage" -delete
	@echo "Cleaned generated files (raw data preserved)."

zip:
	cd /home/claude && zip -r nigeria_dfs_analysis.zip nigeria_dfs_analysis/ \
		--exclude "*/data/raw/*" \
		--exclude "*/__pycache__/*" \
		--exclude "*/.git/*" \
		--exclude "*.pyc"
	@echo "Project zipped: nigeria_dfs_analysis.zip"
