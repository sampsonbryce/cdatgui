#!/usr/bin/env python

from distutils.core import setup

setup(
    name="CDAT GUI",
    version="0.1",
    description="A Graphical User Interface for CDAT",
    author="Sam Fries",
    author_email="fries2@llnl.gov",
    packages=["cdatgui",
              "cdatgui.bases",
              "cdatgui.variables",
              "cdatgui.spreadsheet",
              "cdatgui.graphics"],
    scripts=["scripts/cdatgui"],
    package_data={"cdatgui": ["resources/*.png"]}
)
