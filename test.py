#!/usr/bin/env python

import pytest
import coverage
import os.path

source_path = os.path.join(os.path.dirname(__file__), "cdatgui")

cov = coverage.coverage(source=[source_path], branch=True)

print "Beginning test run..."

cov.start()
pytest.main(["tests"])
cov.stop()

print "Test run complete, saving statistics..."

cov.save()

print "Saving html report..."

cov.html_report(directory="htmlcov")

print "Saved report"
