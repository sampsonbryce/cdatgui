#!/usr/bin/env python

from setuptools import setup, find_packages

import os

setup(
    name="CDAT GUI",
    version="0.1",
    description="A Graphical User Interface for CDAT",
    author="Sam Fries",
    author_email="fries2@llnl.gov",
    packages=find_packages(exclude="tests"),
    package_data={"cdatgui": ["resources/*.*", "resources/pattern_thumbs/*.*"]},
    scripts=["scripts/cdatgui"],
    install_requires=["sqlalchemy>=1.0", "qtconsole>=4.2.1"]
)
