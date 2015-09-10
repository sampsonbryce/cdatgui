#!/usr/bin/env python

import pytest
import coverage
import os.path

source_path = os.path.join(os.path.dirname(__file__), "cdatgui")

cov = coverage.coverage(source=[source_path], branch=True)
cov.start()
pytest.main(["tests"])
cov.stop()
cov.save()

cov.html_report(directory="htmlcov")
