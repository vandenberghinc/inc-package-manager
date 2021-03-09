#!/usr/bin/env python3

# Note!
# ' are required, do not use any '.

# setup.
from setuptools import setup, find_packages
setup(
	name='inc-package-manager',
	version='2.10.0',
	description='Some description.',
	url='http://github.com/vandenberghinc/vandenberghinc-package-manager',
	author='Daan van den Bergh',
	author_email='vandenberghinc.contact@gmail.com',
	license='MIT',
	packages=find_packages(),
	include_package_data=True,
	zip_safe=False,
	install_requires=[
            'cl1>=1.13.2',
            'netw0rk>=1.9.3',
            'r3sponse>=2.10.3',
            'syst3m>=2.16.7',
            'dev0s>=2.16.4',
        ],)