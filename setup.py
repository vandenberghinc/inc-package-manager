#!/usr/bin/env python3

# Note!
# ' are required, do not use any ".

# setup.
from setuptools import setup, find_packages
setup(
	name='inc-package-manager',
	version='2.3.2',
	description='Some description.',
	url="http://github.com/vandenberghinc/vandenberghinc-package-manager",
	author='Daan van den Bergh',
	author_email='vandenberghinc.contact@gmail.com',
	license='MIT',
	packages=find_packages(),
	include_package_data=True,
	zip_safe=False,
	install_requires=[
		#"requests",
	],)