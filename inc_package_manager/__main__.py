#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# insert the package for universal imports.
import os, sys
from dev0s import * ; sys.path.insert(1, Defaults.source_path(__file__, back=2))
from inc_package_manager.classes.config import *
from inc_package_manager import package_manager

# the cli object class.
class CLI_(CLI.CLI):
	def __init__(self):
		
		# defaults.
		CLI.CLI.__init__(self,
			modes={
				"--install package-name":"Install a package.",
				"--uninstall package-name":"Uninstall a package.",
				"--update [optional: package-name]":"Update all packages, optionally specify one package to update.",
				"--version package-name [optional: --remote]":"Retrieve the installed / remote version of a package.",
				"--requirements package-name [optional: --remote]":"Retrieve the installed / remote version of a package in requirements format.",
				"--config":f"Configure the {ALIAS}.",
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
		self.arguments.check(exceptions=["--log-level", "--create-alias", "--version", "--remote"], json=Defaults.options.json)

		# help.
		if self.arguments.present(['-h', '--help']):
			self.docs(success=True, json=Defaults.options.json)

		# config.
		elif self.arguments.present('--config'):
			loader = Console.Loader(f"Updating the configuration setttings")
			edits = 0
			api_key = self.arguments.get('--api-key', required=False, json=Defaults.options.json)
			if api_key != None:
				package_manager.configuration.dictionary["api_key"] = api_key
				edits += 1 
			if edits == 0:
				loader.stop()
				os.system(f"nano {package_manager.configuration.fp.path}")
			if edits > 0:
				package_manager.configuration.save()
				loader.stop()
				self.stop(message=f"Successfully saved {edits} edit(s).", json=Defaults.options.json)
			#else:
			#	loader.stop(success=False)
			#	self.stop(error=f"Speficy one of the configuration arguments to edit. Run ($ {ALIAS} -h) for more info.", json=Defaults.options.json)

		# install a package.
		elif self.arguments.present('--install'):
			self.stop(response=package_manager.install(self.arguments.get('--install')), json=Defaults.options.json)

		# uninstall a package.
		elif self.arguments.present('--uninstall'):
			package = self.arguments.get('--uninstall', json=Defaults.options.json)
			if not self.arguments.present(["-y", "--assume-yes"]) and not Defaults.options.json and not Console.input(f"&ORANGE&Warning!&END& You are uninstalling package {_package_}. Do you wish to proceed?", yes_no=True):
				self.stop(message="Aborted.")
			self.stop(response=package_manager.uninstall(package), json=Defaults.options.json)

		# update a package.
		elif self.arguments.present('--update'):
			package = self.arguments.get('--update', required=False, json=Defaults.options.json)
			if package == None: package = "all"
			self.stop(response=package_manager.update(package), json=Defaults.options.json)

		# get the version of a package.
		elif self.arguments.present(['--version', "--requirements"]):
			package = self.arguments.get('--version', json=Defaults.options.json)
			remote = self.arguments.present("--remote")
			response = package_manager.version(package)
			if not response["success"]:
				self.stop(response=response, json=Defaults.options.json)
			else:
				if self.arguments.present(["--requirements"]):
					self.stop(message=f"{package}=={response.version}", json=Defaults.options.json)
				else:
					self.stop(message=f"{package} version: {response.version}", json=Defaults.options.json)

		# invalid.
		else: self.invalid(json=Defaults.options.json)

		#
	
# main.
if __name__ == "__main__":
	cli = CLI_()
	cli.start()
