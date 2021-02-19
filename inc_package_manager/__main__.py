#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# insert the package for universal imports.
import os, sys, syst3m ; sys.path.insert(1, syst3m.defaults.source_path(__file__, back=2))
from inc_package_manager.classes.config import *
from inc_package_manager.classes import *

# the cli object class.
class CLI(cl1.CLI):
	def __init__(self):
		
		# defaults.
		cl1.CLI.__init__(self,
			modes={
				"--install package-name":"Install a package.",
				"--uninstall package-name":"Uninstall a package.",
				"--update [optional: package-name]":"Update all packages, optionally specify one package to update.",
				"--version packge-name [optional: --remote]":"Retrieve the installed / remote version of a package.",
				"--config":"Configure the package-manager.",
				"   --api-key your-api-key":"Specify your vandenberghinc api key.",
				"-h / --help":"Show the documentation.",
			},
			options={
				#"-y / --assume-yes":"Do not prompt for the [Are you sure] warning.",
			},
			alias=ALIAS,
			executable=__file__,
		)

		#
	def start(self):

		# check arguments.
		JSON = False
		self.arguments.check(exceptions=["--log-level", "--create-alias", "--version"], json=JSON)

		# help.
		if self.arguments.present(['-h', '--help']):
			self.docs(success=True, json=JSON)

		# version.
		elif self.arguments.present(['--version']):
			print(f"{ALIAS} version:",Files.load(f"{SOURCE_PATH}/.version").replace("\n",""))

		# config.
		elif self.arguments.present('--config'):
			loader = syst3m.console.Loader(f"Updating the configuration setttings")
			edits = 0
			api_key = self.arguments.get('--api-key', required=False)
			if api_key != None:
				package_manager.configuration.dictionary["api_key"] = api_key
				edits += 1 
			if edits > 0:
				package_manager.configuration.save()
				loader.stop()
			else:
				loader.stop(success=False)
				r3sponse.log(error="Speficy one of the configuration arguments to edit. Run ($ package-manager -h) for more info.")

		# install a package.
		elif self.arguments.present('--install'):
			package_manager.install(self.arguments.get('--install'))

		# uninstall a package.
		elif self.arguments.present('--uninstall'):
			package_manager.uninstall(self.arguments.get('--uninstall'))

		# install a package.
		elif self.arguments.present('--update'):
			package = self.arguments.get('--update', required=False)
			if package == None: package = "all"
			package_manager.update(package)

		# install a package.
		elif self.arguments.present('--version'):
			package = self.arguments.get('--version')
			remote = self.arguments.present("--remote")
			response = package_manager.version(package, remote=remote)
			if not response.success: print(response.error)
			else:
				if remote: 
					print(f"{package}{remote}: {response.remote_version}")
				else: 
					print(f"{package} remote: {response.current_version}")

		# invalid.
		else: 
			print(self.documentation)
			r3sponse.log(error="Selected an invalid mode.")

		#
	
# main.
if __name__ == "__main__":
	cli = CLI()
	cli.start()
