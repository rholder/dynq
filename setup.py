#!/usr/bin/env python
import sys

from setuptools import setup

requires = ['boto==2.28.0',
            'click==0.7']

py_modules = ['dynamo_ftw']
packages = []

setup_options = dict(
    name='dynamo_ftw',
    version='0.1.0',
    description='Simple standalone DynamoDB client',
    author='Ray Holder',
    author_email='',
    install_requires=requires,
    py_modules=py_modules,
    packages=packages
)

setup(**setup_options)
