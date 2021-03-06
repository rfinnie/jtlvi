#!/usr/bin/env python3

import os
import sys
from setuptools import setup, find_packages

assert sys.version_info > (3, 4)


def read(filename):
    with open(os.path.join(os.path.dirname(__file__), filename), encoding="utf-8") as f:
        return f.read()


setup(
    name="jtlvi",
    description="JTLVI Message Format: Just TLV It!",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    version="1.0.1",
    license="BSD",
    platforms=["Unix"],
    author="Ryan Finnie",
    author_email="ryan@finnie.org",
    url="https://github.com/rfinnie/jtlvi",
    download_url="https://github.com/rfinnie/jtlvi",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    test_suite="tests",
)
