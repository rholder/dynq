#!/usr/bin/env python
from setuptools import setup

requirements_lines = [line.strip() for line in open('requirements.txt').readlines()]
requires = list(filter(None, requirements_lines))

py_modules = ['dynq.dynq', 'dynq.boto_monkey']
packages = []

setup_options = dict(
    name='dynq',
    version='0.2.2',
    description='Simple standalone DynamoDB client',
    author='Ray Holder',
    author_email='',
    install_requires=requires,
    py_modules=py_modules,
    packages=packages
)

setup(**setup_options)
