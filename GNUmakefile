.PHONY: help test check clean dist install

VERSION = $(shell $(PYTHON) -c "import aspects; print \".\".join(str(s) for s in aspects.version_info)")

PYTHON ?= python

help:
	@echo "make check   - run unit tests"
	@echo "make clean   - remove unnecessary files"
	@echo "make dist    - create dist/aspects-$(VERSION).tar.gz*"
	@echo "make install - install to the system's site-packages*"
	@echo "*) runs $(PYTHON) setup.py"
	@echo ""
	@echo "Define Python version with the PYTHON environment variable."
	@echo "Example: PYTHON=python2.6 make install"

check:
	@for f in test/test_*.py; do \
		echo "---- $$f"; \
		PYTHONPATH=`pwd` $(PYTHON) $$f || exit $?; \
	done

dist:
	$(PYTHON) setup.py sdist

install:
	$(PYTHON) setup.py install

clean:
	$(RM) *.pyc *~ */*.pyc */*~
	$(RM) -r build dist