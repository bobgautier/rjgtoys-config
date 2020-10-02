#!/usr/bin/python3

from rjgtoys.projects import setup


setup(
    name = "rjgtoys.config",
    version = "0.0.1",
    author = "Bob Gautier",
    author_email = "bob.gautier@gmail.com",
    description = ("A modular interface for configuration data"),
    license = "GPL",
    keywords = "configuration",
    namespace_packages=['rjgtoys'],
    packages = ['rjgtoys.config'],
    classifiers = [
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)"
        ],
)
