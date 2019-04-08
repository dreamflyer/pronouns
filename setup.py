#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='pronouns',
      version='0.0.1',
      description='This package has shared components.',
      author='Dreamflyer',
      author_email='user@email.com',
      packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
      license='LICENSE.txt',
    )
