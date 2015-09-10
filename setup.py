#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name="CDAT GUI",
    version="0.1",
    description="A Graphical User Interface for CDAT",
    author="Sam Fries",
    author_email="fries2@llnl.gov",
    packages=find_packages(exclude="tests"),
    scripts=["scripts/cdatgui"],
    package_data={"cdatgui": ["resources/*"]},
    install_requires=["sqlalchemy>=1.0"]
)
