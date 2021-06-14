.PHONY: install-pynq install-pc uninstall-pc export-pc docs clean lint run-streamlit run-yolo-pc run-yolo-pynq mqtt-docker help

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
PROJECT_NAME = pynq
PYTHON_INTERPRETER = python
CONDA_ENV_FILE = config/pc/condaenv.yml
CONDA_ENV_NAME = mas_env
DASHBOARD_DIR = src/streamlit
DASHBOARD_ENTRY = app.py
YOLO_SCRIPT = src/yolo/people_detection.py
DOCSBUILDDIR = docs/_build

ifeq (,$(shell where conda))
HAS_CONDA=False
else
HAS_CONDA=True
SEARCH_ENV=$(shell conda.bat info --envs | grep $(CONDA_ENV_NAME))
FOUND_ENV_NAME = $(word 1, $(notdir $(SEARCH_ENV)))
# check if conda environment is active
ifneq ($(CONDA_DEFAULT_ENV),$(FOUND_ENV_NAME))
	CONDA_ACTIVATE := source $$(conda.bat info --base)/etc/profile.d/conda.sh ; conda activate $(CONDA_ENV_NAME)
else
    CONDA_ACTIVATE := true
endif
endif

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Install the kernel user wide and the local python package
install-pynq:
	@pip3 install -r config/pynq/pip_requirements.txt

install-pc:
ifeq (True,$(HAS_CONDA))
ifneq ($(FOUND_ENV_NAME),)
	@echo ">>> Found $(CONDA_ENV_NAME) environment. Skipping installation..."
else
	@echo ">>> Creating conda environment $(CONDA_ENV_NAME)"
	@conda env create -f $(CONDA_ENV_FILE) -n $(CONDA_ENV_NAME)
endif
else
	@echo ">>> Please install Anaconda you mammal!"
endif

## Uninstall environment
uninstall-pc:
	@$(CONDA_ACTIVATE); conda env remove --name $(CONDA_ENV_NAME)
	@echo ">>> Environment '$(CONDA_ENV_NAME)' removed."

## Update conda environnement (usefull when the env file contains changes)
update-pc:
	@$(CONDA_ACTIVATE); conda env update -n $(CONDA_ENV_NAME) -f $(CONDA_ENV_FILE)
	@echo ">>> Environment updated from '$(CONDA_ENV_FILE)'."

.ONESHELL:
conda-export:
	@$(CONDA_ACTIVATE)
	@conda env export > $(CONDA_ENV_FILE)
	@echo ">>> Environment file '$(CONDA_ENV_FILE)' exported."

## Build sphinx docs
.ONESHELL:
docs:
	@$(CONDA_ACTIVATE)
	$(MAKE) -C docs html

## Delete all compiled Python files
clean:
	find . -type f -name "*.py[co]" -delete
	find . -type d -name "__pycache__" -delete
	@rm -rf dist build
	@make -C docs clean

## Lint using flake8
lint:
	@$(CONDA_ACTIVATE); flake8 src

## Start the dashboard application
run-streamlit:
	@$(CONDA_ACTIVATE); cd $(DASHBOARD_DIR); streamlit run $(DASHBOARD_ENTRY)

run-yolo-pc:
	@@$(CONDA_ACTIVATE); $(PYTHON_INTERPRETER) $(YOLO_SCRIPT)

run-yolo-pynq:
	@sudo python3 $(YOLO_SCRIPT)

docker:
	@docker run -it -p 1883:1883 -p 9001:9001 eclipse-mosquitto:1.6

help: docs
	@python -c "import os;os.system('start $(DOCSBUILDDIR)/html/index.html')"
