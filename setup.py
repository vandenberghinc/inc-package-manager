#!/usr/bin/env python3

# Note!
# ' are required, do not use any '.

# setup.
from setuptools import setup, find_packages
setup(
	name='inc-package-manager',
	version='2.8.9',
	description='Some description.',
	url='http://github.com/vandenberghinc/vandenberghinc-package-manager',
	author='Daan van den Bergh',
	author_email='vandenberghinc.contact@gmail.com',
	license='MIT',
	packages=find_packages(),
	include_package_data=True,
	zip_safe=False,
	install_requires=[
            'cl1>=1.11.8',
            'netw0rk>=1.7.5',
            'r3sponse>=2.8.6',
            'syst3m>=2.13.2',
            'fil3s>=2.12.8',
        ],)