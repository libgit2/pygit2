.PHONY: build

build:
	python setup.py build_ext --inplace

html:
	cd docs && find . -name "*rst" | entr make html
