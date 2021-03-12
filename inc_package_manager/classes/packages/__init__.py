#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# imports.
from inc_package_manager.classes.config import *

# the manager class.
class PackageManager(object):
	def __init__(self):	

		# checks.
		if not os.path.exists(f"/etc/{ALIAS}"):
			dev0s.response.log(f"&ORANGE&Root permission&END& required to create {ALIAS} database [/etc/{ALIAS}].")
			os.system(f"sudo mkdir /etc/{ALIAS} && sudo chown {dev0s.defaults.vars.user}:{dev0s.defaults.vars.group} /etc/{ALIAS} && sudo chmod 770 /etc/{ALIAS}")

		# config.
		self.configuration = Dictionary(path=f"/etc/{ALIAS}/config", load=True, default={
				"api_key":None,
			})

		# api key (do not make it a property).
		self.api_key = self.configuration.dictionary["api_key"]

		# remote info.
		self.packages = {}
		self.versions = {}
		self.__download_packages_info__() # also tests connection.

		#

	# installating packages.
	def installed(self, package):
		package = self.__package_identifier__(package)
		if package not in list(self.packages.keys()):
			return dev0s.response.error(f"Package [{package} does not exist.")
		if package in [ALIAS, ALIAS.replace("-","_")]:
			installed = True
		elif self.packages[package]["library"] not in ["", None, False]:
			path = self.packages[package]["library"]
			installed = Files.exists(path)
		else:
			return dev0s.response.error(f"Unable to determine if package {package} is installed.")
		return dev0s.response.success(f"Successfully checked if package [{package}] is installed.", {
			"installed":installed,
		})
	def install(self, 
		# the package id (str) (#1).
		package, 
		# the post install arguments (str).
		post_install_args="", 
		# stable or unstable release (bool).
		stable=True, 
		# specific version (str) (leave None to use the lastest).
		version=None, 
		# the log levenl (int).
		log_level=dev0s.defaults.options.log_level,
	):
		
		# check & version.
		response = self.version(package, remote=True, log_level=log_level)
		if not response.success: return response
		rversion, lversion = response.version, None
		if version != None: rversion = version
		version_str = f"({rversion})"
		response = self.version(package, remote=False, log_level=log_level)
		if response.success:
			lversion = response.version
			version_str = f"({lversion}) ==> ({rversion})"

		# loader.
		if log_level >= 0: loader = dev0s.console.Loader(f"Preparing package installation {package} {version_str}")

		# package settings.
		free, library, post_install = self.packages[package]["free"], self.packages[package]["library"], self.packages[package]["post_install"]

		# check api key.
		if not free and self.api_key == None:
			if log_level >= 0: loader.stop(success=False)
			return dev0s.response.error(f"Specify your vandenberghinc api key to install library {package}, execute [$ {ALIAS} --config --api-key your-api-key].")

		# install package.
		if post_install in [None, False, ""]:
			fp = FilePath(self.packages[package]["library"])
			if fp.exists():
				try: os.remove(fp.path)
				except PermissionError: 
					#if log_level >= 0: loader.hold()
					print(f"{color.orange}Root permission{color.end} required to reinstall package {package}.")
					fp.delete(forced=True, sudo=True)
					#if log_level >= 0: loader.release()

		# init zip.
		zip = Zip(f"/tmp/{package}.zip")
		extract_dir = Files.Directory(path=f"/tmp/{package}.extract/")
		extract_dir.fp.delete(forced=True)
		zip.fp.delete(forced=True)
		os.system(f"rm -fr /tmp/{package}/")
		tmp_dir = Files.Directory(path=f"/tmp/{package}/")

		# make request.
		if log_level >= 0: loader.mark(new_message=f"Downloading package {package} {version_str}")
		response_object = self.request("/packages/download/", {
			"package":package,
			"stable":stable,
			"version":version,
		}, json=False)

		# handle status code.
		if response_object.status_code != 200:
			return dev0s.response.error(f"Failed to install package {package} {version_str} [{response_object.status_code}] (/packages/download/).")	

		# check json applicaton.
		if "application/json" in response_object.headers["content-type"] :

			# handle response.
			try: response = dev0s.response.ResponseObject(response_object.json())	
			except: 
				try: response = dev0s.response.ResponseObject(response_object.json())
				except:
					if log_level >= 0: loader.stop(success=False)
					try:
						return dev0s.response.error(f"Failed to install package {package} {version_str}. Unable to serialze output (json): {response_object.json()}")
					except:
						return dev0s.response.error(f"Failed to install package {package} {version_str}. Unable to serialze output (txt): {response_object.txt}")
			if log_level >= 0: loader.stop(success=response["success"])
			return response	
			#if not response.success:
			#	if log_level >= 0: loader.stop(success=False)
			#	return dev0s.response.error(f"Failed to install package {package}, error: {response['error']}")	

		# check unkown applicaton.
		elif "application/force-download" not in response_object.headers["content-type"]:
			return dev0s.response.error(f"Failed to install package {package} {version_str}, unkown response application: {response_object.headers['content-type']}")	

		# write out.
		if log_level >= 0: loader.mark(new_message=f"Writing out package {package} {version_str}")
		try:
			open(zip.file_path.path, 'wb').write(response_object.content)
		except Exception as e:
			if log_level >= 0: loader.stop(success=False)
			return dev0s.response.error(f"Failed to install package {package} {version_str}, error: {e}.")	
		if not zip.file_path.exists():
			if log_level >= 0: loader.stop(success=False)
			return dev0s.response.error(f"Failed to install package {package} {version_str}, failed to write out {zip.file_path.path}.")

		# extract.
		if log_level >= 0: loader.mark(new_message=f"Extracting package {package} {version_str}")
		zip.extract(base=extract_dir.file_path.path)
		paths = extract_dir.paths(recursive=False)
		if len(paths) == 0:
			if log_level >= 0: loader.stop(success=False)
			extract_dir.fp.delete(forced=True)
			tmp_dir.fp.delete(forced=True)
			return dev0s.response.error(f"Failed to install package {package} {version_str}, found no packages while extracting.")
		elif len(paths) > 1:
			if log_level >= 0: loader.stop(success=False)
			extract_dir.fp.delete(forced=True)
			tmp_dir.fp.delete(forced=True)
			return dev0s.response.error(f"Failed to install package {package} {version_str}, found multiple packages while extracting.")
		os.system(f"mv {paths[0]} {tmp_dir.file_path.path}")
		if not tmp_dir.file_path.exists():
			if log_level >= 0: loader.stop(success=False)
			extract_dir.fp.delete(forced=True)
			tmp_dir.fp.delete(forced=True)
			return dev0s.response.error(f"Failed to install package {package} {version_str}, failed to write out {tmp_dir.file_path.path}.")

		# post installation.
		if post_install not in [None, False, ""]:
			if log_level >= 0: loader.mark(new_message=f"Executing post installation script of package {package} {version_str}")
			os.system(f'chmod +x {tmp_dir.file_path.path}{post_install}')
			print(f"{color.orange}Root permission{color.end} required to install package {package}.")
			#if log_level >= 0: loader.hold()
			#os.system("sudo ls | grep ASJKBKJBkjuiyy89y23smndbKUy3hkjNMADBhje")
			#if log_level >= 0: loader.release()
			#command = f"sudo -u {dev0s.defaults.vars.user} bash {tmp_dir.file_path.path}{post_install} {post_install_args}"
			os.system('sudo echo "" > /dev/null')
			command = f"bash {tmp_dir.file_path.path}{post_install} {post_install_args}"
			#output = dev0s.utils.__execute_script__(command)
			response = dev0s.code.execute(command)
			if not response.success: 
				if log_level >= 0: loader.stop(success=False)
				extract_dir.fp.delete(forced=True)
				tmp_dir.fp.delete(forced=True)
				return response
			output = response.output
			if "Successfully installed " in output:
				if log_level >= 0: loader.stop()
				if log_level >= 1: print(output)
				extract_dir.fp.delete(forced=True)
				tmp_dir.fp.delete(forced=True)
				return dev0s.response.success(f"Successfully installed package {package} {version_str}.")
			else:
				if log_level >= 0: loader.stop(success=False)
				extract_dir.fp.delete(forced=True)
				tmp_dir.fp.delete(forced=True)
				return dev0s.response.error(f"Failed to install package {package} {version_str}, failed to run the post installation script output: \n{output}.")
		else:
			os.system(f"mv {tmp_dir.file_path.path} {library}")
			if tmp_dir.file_path.exists():
				if log_level >= 0: loader.stop()
				extract_dir.fp.delete(forced=True)
				tmp_dir.fp.delete(forced=True)
				return dev0s.response.success(f"Successfully installed package {package} {version_str}.")
			else:
				if log_level >= 0: loader.stop(success=False)
				extract_dir.fp.delete(forced=True)
				tmp_dir.fp.delete(forced=True)
				return dev0s.response.error(f"Failed to install package {package} {version_str}, failed to move the library to {library}.")

		#

	# uninstalling packages.
	def uninstall(self, 
		# the package id (str) (#1).
		package, 
		# the log levenl (int).
		log_level=dev0s.defaults.options.log_level,
	):

		# check & version.
		response = self.version(package, log_level=log_level)
		if not response.success: return response
		version = response.version

		# loader.
		if log_level >= 0: loader = dev0s.console.Loader(f"Uninstalling package {package} ({version})")

		# delete package.
		if self.packages[package]["library"] not in ["", None, False]:
			file_path = FilePath(self.packages[package]["library"])
			if file_path.exists():
				try: os.remove(file_path.path)
				except PermissionError: file_path.delete(forced=True, sudo=True)
			if file_path.exists():
				if log_level >= 0: loader.stop(success=False)
				return dev0s.response.error(f"Failed to uninstall package {package}.")

		# alias.
		os.system(f"rm -fr /usr/local/bin/{package}")

		# success.
		if log_level >= 0: loader.stop()
		return dev0s.response.success(f"Successfully uninstalled package {package}.")

		#

	# get the package version.
	def version(self, 
		# the package id (str) (#1).
		package, 
		# the remote or local version (bool) (remote False ignores parameter [stable]).
		remote=False, 
		# stable or unstable release (bool).
		stable=True, 
		# the log levenl (int).
		log_level=dev0s.defaults.options.log_level,
	):
		# checks.
		package = self.__package_identifier__(package)
		if package not in list(self.packages.keys()):
			return dev0s.response.error(f"Specified package [{package} does not exist.")

		# remote.
		if remote:
			remote_str = "remote "

			# stable.
			if stable:
				stable_str = "stable "
				version = self.versions["unstable"][package]["newest"]

			# unstable.
			else:
				stable_str = ""
				version = self.versions["unstable"][package]["newest"]

		# local.
		else:
			stable_str = ""
			remote_str = ""
			if package in [ALIAS, ALIAS.replace("-","_")]:
				path = f'{SOURCE}/.version'
				if not Files.exists(path):
					return dev0s.response.error(f"Failed to retrieve the version of package {package}.")
				version = Files.load(path).replace("\n","")
			elif self.packages[package]["library"] not in ["", False, None]:
				path = f'{self.packages[package]["library"]}/.version'
				if not Files.exists(path):
					return dev0s.response.error(f"Failed to retrieve the version of package {package} [{path}].")
				version = Files.load(path).replace("\n","")
			else:
				return dev0s.response.error(f"Failed to retrieve the version of package {package}.")

		# handler.
		return dev0s.response.success(f"Successfully retrieved the {stable_str}{remote_str}version of package {package}.", {
			"version":version,
		})

		#

	# updating packages.
	def update(self, 
		# the package id (str) (#1).
		package="all", 
		# the post install arguments (str).
		post_install_args="", 
		# stable or unstable release (bool).
		stable=True, 
		# the log levenl (int).
		log_level=dev0s.defaults.options.log_level,
	):
		# update all recursive.
		if package == "all":
			c, u = 0, 0
			for package, info in self.packages.items():
				response = self.installed(package)
				if not response.success: return response
				elif response.installed:
					response = self.update(package, stable=stable)
					if response["error"] != None and "already up-to-date" not in response["error"].lower(): return response
					elif response.success:
						if "already up-to-date" in response.message: 
							u += 1
						else:
							c += 1
			if c != 0 and u != 0:
				return dev0s.response.success(f"Successfully updated {c} package(s).")
			elif c != 0:
				return dev0s.response.success(f"Successfully updated {c} package(s).")
			elif u != 0:
				return dev0s.response.success(f"All {u} installed package(s) are already up-to-date.")
			else:
				return dev0s.response.success(f"There are no packages installed.")
		# update package.
		else:
			# check & version.
			response = self.installed(package)
			if not response.success: return response
			elif response.installed:
				return dev0s.response.error(f"Package [{package} is not installed.")
			response = self.version(package, log_level=log_level, stable=stable)
			if not response.success: return response
			version = response.version
			response = self.version(package, remote=True, stable=stable)
			if response["error"] != None: 
				return response
			remote_version = response.version
			if version == remote_version:
				return dev0s.response.success(f"Package {package} is already up-to-date ({version}=={remote_version}).")
			response = self.install(package, post_install_args=post_install_args, stable=stable)
			if response["error"] != None: return response
			return dev0s.response.success(f"Successfully updated package {package} ({version}) ==> ({remote_version}).")

	# reloads the remote packages info.
	def up_to_date(self,
		# the package id (str) (#1). 
		package,
		# stable or unstable release (bool).
		stable=True, 
		# the log levenl (int).
		log_level=dev0s.defaults.options.log_level,
		# 
	):
		response = self.installed(package)
		if not response.success: return response
		elif response.installed:
			return dev0s.response.error(f"Package [{package} is not installed.")
		self.__download_packages_info__()
		response = self.version(package, remote=True, stable=stable, log_level=log_level)
		if response["error"] != None: return response
		remote_version = response.version
		response = self.version(package, remote=False, stable=stable, log_level=log_level)
		if response["error"] != None: 
			return response
		up_to_date = response.version == remote_version
		return dev0s.response.success(f"Successfully compared the versions of package {package}.", {
			"up_to_date":up_to_date,
			"current_version":response.version,
			"remote_version":remote_version,
			"stable":stable,
		})

	# make api.vandenberghinc.com request.
	def request(self, url="/", data={}, json=True):

		# url.
		url = f"api.vandenberghinc.com/{gfp.clean(url, remove_first_slash=True, remove_last_slash=True)}/"
		data["api_key"] = self.api_key
		return dev0s.requests.get(url=url, data=data, serialize=json)

		#

	# system functions.
	def __package_identifier__(self, package):
		return package.replace(" ","-")
		#
	def __download_packages_info__(self):
		response = self.request("/packages/list/")
		if not response.success: raise ValueError(f"Failed to download the vandenberghinc packages, error: {response['error']}")
		self.packages = response["packages"]
		response = self.request("/packages/versions/", {"stable":False})
		if not response.success: raise ValueError(f"Failed to download stable vandenberghinc versions, error: {response['error']}")
		self.versions["unstable"] = response.versions
		response = self.request("/packages/versions/", {"stable":True})
		if not response.success: raise ValueError(f"Failed to download unstable vandenberghinc versions, error: {response['error']}")
		self.versions["stable"] = response.versions

	#

# initialized class.
package_manager = PackageManager()
