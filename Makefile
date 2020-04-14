.PHONY: build html

build:
	python setup.py build_ext --inplace -g

html:
	cd docs && find . -name "*rst" | entr make html
