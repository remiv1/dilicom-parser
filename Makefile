PYTHON ?= $(if $(wildcard ./venv/bin/python),./venv/bin/python,python3)
PIP ?= $(PYTHON) -m pip

DOCS_SRC_DIR ?= documentations/sphinxdoc
DOCS_BUILD_DIR ?= $(DOCS_SRC_DIR)/_build/html
DOCS_PUBLISH_DIR ?= docs
DIST_DIR ?= dist

.PHONY: help docs update-docs build check upload release clean

help:
	@echo "Cibles disponibles:"
	@echo "  make docs         - Génère la documentation Sphinx et met à jour docs/"
	@echo "  make build        - Construit les artefacts de package (sdist/wheel)"
	@echo "  make check        - Vérifie les artefacts avec twine check"
	@echo "  make upload       - Upload des artefacts sur l'index Python (twine upload)"
	@echo "  make release      - Enchaîne docs + build + check + upload"
	@echo "  make clean        - Nettoie les artefacts de build"

update-docs docs:
	$(MAKE) -C $(DOCS_SRC_DIR) html
	mkdir -p $(DOCS_PUBLISH_DIR)
	cp -r $(DOCS_BUILD_DIR)/* $(DOCS_PUBLISH_DIR)/

build: clean
	$(PYTHON) -m build

check: build
	$(PYTHON) -m twine check $(DIST_DIR)/*

upload:
	$(PYTHON) -m twine upload $(DIST_DIR)/*

release: build docs check upload

clean:
	rm -rf build $(DIST_DIR) *.egg-info
	rm -rf src/*.egg-info
	rm -rf $(DOCS_SRC_DIR)/_build
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	
