#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# insert the package for universal imports.
import os, sys, syst3m ; sys.path.insert(1, syst3m.defaults.source_path(__file__, back=2))
from inc_package_manager.classes.config import *
from inc_package_manager import package_manager

# the cli object class.
class CLI(cl1.CLI):
	def __init__(self):
		
		# defaults.
		cl1.CLI.__init__(self,
			modes={
				"--install package-name":"Install a package.",
				"--uninstall package-name":"Uninstall a package.",
				"--update [optional: package-name]":"Update all packages, optionally specify one package to update.",
				"--version package-name [optional: --remote]":"Retrieve the installed / remote version of a package.",
				"--requirements package-name [optional: --remote]":"Retrieve the installed / remote version of a package in requirements format.",
				"--config":"Configure the package-manager.",
				"   --api-key your-api-key":"Specify your vandenberghinc api key.",
				"-h / --help":"Show the documentation.",
			},
			options={
				"-y / --assume-yes":"Do not prompt for the [Are you sure] warning.",
				"-j / --json":"Print the response in json format.",
				"--log-level <int>":"Overwrite the default log levels.",
			},
			alias=ALIAS,
			executable=__file__,
		)

		#
	def start(self):

		# check arguments.
		self.arguments.check(exceptions=["--log-level", "--create-alias", "--version", "--remote"], json=JSON)

		# help.
		if self.arguments.present(['-h', '--help']):
			self.docs(success=True, json=JSON)

		# config.
		elif self.arguments.present('--config'):
			loader = syst3m.console.Loader(f"Updating the configuration setttings")
			edits = 0
			api_key = self.arguments.get('--api-key', required=False, json=JSON)
			if api_key != None:
				package_manager.configuration.dictionary["api_key"] = api_key
				edits += 1 
			if edits > 0:
				package_manager.configuration.save()
				loader.stop()
				self.stop(message=f"Successfully saved {edits} edit(s).", json=JSON)
			else:
				loader.stop(success=False)
				self.stop(error="Speficy one of the configuration arguments to edit. Run ($ package-manager -h) for more info.", json=JSON)

		# install a package.
		elif self.arguments.present('--install'):
			self.stop(response=package_manager.install(self.arguments.get('--install')), json=JSON)

		# uninstall a package.
		elif self.arguments.present('--uninstall'):
			package = self.arguments.get('--uninstall', json=JSON)
			if not self.arguments.present(["-y", "--assume-yes"]) and not JSON and not syst3m.console.input(f"&ORANGE&Warning!&END& You are uninstalling package {_package_}. Do you wish to proceed?", yes_no=True):
				self.stop(message="Aborted.")
			self.stop(response=package_manager.uninstall(package), json=JSON)

		# update a package.
		elif self.arguments.present('--update'):
			package = self.arguments.get('--update', required=False, json=JSON)
			if package == None: package = "all"
			self.stop(response=package_manager.update(package), json=JSON)

		# get the version of a package.
		elif self.arguments.present(['--version', "--requirements"]):
			package = self.arguments.get('--version', json=JSON)
			remote = self.arguments.present("--remote")
			response = package_manager.version(package)
			if not response["success"]:
				self.stop(response=response, json=JSON)
			else:
				if self.arguments.present(["--requirements"]):
					self.stop(message=f"{package}=={response.version}", json=JSON)
				else:
					self.stop(message=f"{package} version: {response.version}", json=JSON)

		# invalid.
		else: self.invalid(json=JSON)

		#
	
# main.
if __name__ == "__main__":
	cli = CLI()
	cli.start()
