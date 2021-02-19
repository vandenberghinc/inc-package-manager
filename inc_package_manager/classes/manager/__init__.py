#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# imports.
from inc_package_manager.classes.config import *

# the manager class.
class PackageManager(object):
	def __init__(self):	
		self.packages = {}
		self.__download_packages_info__() # also tests connection.
		try: 
			self.configuration = Files.Dictionary("/etc/package-manager/config", load=True, default={
					"api_key":None,
				})
			self.api_key = self.configuration.dictionary["api_key"]
		except: 
			self.configuration = None
			self.api_key = None
	def install(self, package, post_install_args="", log_level=0):
		
		# loader.
		if log_level >= 0: loader = syst3m.console.Loader(f"Checking package {package}")

		# check package.
		package = self.__package_identifier__(package)
		if package not in list(self.packages.keys()):
			if log_level >= 0: loader.stop(success=False)
			return r3sponse.error_response(f"Specified package [{package} does not exist.", log_level=log_level)

		# package settings.
		free, library, post_install = self.packages[package]["free"], self.packages[package]["library"], self.packages[package]["post_install"]


		# check api key.
		if not free and self.api_key == None:
			if log_level >= 0: loader.stop(success=False)
			return r3sponse.error_response(f"Specify your vandenberghinc api key to install library {package}, execute [$ package-manager --config --api-key your-api-key].", log_level=log_level)

		# install package.
		if post_install in [None, False, ""]:
			fp = Formats.FilePath(self.packages[package]["library"])
			if fp.exists():
				try: os.remove(fp.path)
				except PermissionError: 
					print(f"{syst3m.color.orange}Root permission{syst3m.color.end} required to reinstall package {package}.")
					if log_level >= 0: loader.hold()
					fp.delete(forced=True, sudo=True)
					if log_level >= 0: loader.release()

		# init zip.
		zip = Files.Zip(f"/tmp/{package}.zip")
		extract_dir = Files.Directory(path=f"/tmp/{package}.extract/")
		extract_dir.fp.delete(forced=True)
		zip.fp.delete(forced=True)
		os.system(f"rm -fr /tmp/{package}/")
		tmp_dir = Files.Directory(path=f"/tmp/{package}/")

		# make request.
		if log_level >= 0: loader.mark(new_message=f"Downloading package {package}")
		response_object = self.__request__("/packages/download/", {
			"package":package,
			"format":"zip",
			"api_key":self.api_key,
		}, json=False)

		# handle status code.
		if response_object.status_code != 200:
			return r3sponse.error_response(f"Failed to install package [{package}], api status code: {response_object.status_code} (/packages/download/).", log_level=log_level)	

		# check json applicaton.
		if response_object.headers["content-type"] == "application/json":

			# handle response.
			try: response = response_object.json()
			except:
				if log_level >= 0: loader.stop(success=False)
				return r3sponse.error_response(f"Failed to install package [{package}], response: {response_object}.", log_level=log_level)	
			if not r3sponse.success(response):
				if log_level >= 0: loader.stop(success=False)
				return r3sponse.error_response(f"Failed to install package [{package}], error: {response['error']}", log_level=log_level)	

		# check unkown applicaton.
		if response_object.headers["content-type"] != "application/force-download":
			return r3sponse.error_response(f"Failed to install package [{package}], unkown response application: {response_object.headers['content-type']}", log_level=log_level)	

		# write out.
		if log_level >= 0: loader.mark(new_message=f"Writing out package {package}")
		try:
			open(zip.file_path.path, 'wb').write(response_object.content)
		except Exception as e:
			if log_level >= 0: loader.stop(success=False)
			return r3sponse.error_response(f"Failed to install package [{package}], error: {e}.", log_level=log_level)	
		if not zip.file_path.exists():
			if log_level >= 0: loader.stop(success=False)
			return r3sponse.error_response(f"Failed to install package [{package}], failed to write out {zip.file_path.path}.", log_level=log_level)

		# extract.
		if log_level >= 0: loader.mark(new_message=f"Extracting package {package}")
		zip.extract(base=extract_dir.file_path.path)
		paths = extract_dir.paths(recursive=False)
		if len(paths) == 0:
			if log_level >= 0: loader.stop(success=False)
			extract_dir.fp.delete(forced=True)
			tmp_dir.fp.delete(forced=True)
			return r3sponse.error_response(f"Failed to install package [{package}], found no packages while extracting.", log_level=log_level)
		elif len(paths) > 1:
			if log_level >= 0: loader.stop(success=False)
			extract_dir.fp.delete(forced=True)
			tmp_dir.fp.delete(forced=True)
			return r3sponse.error_response(f"Failed to install package [{package}], found multiple packages while extracting.", log_level=log_level)
		os.system(f"mv {paths[0]} {tmp_dir.file_path.path}")
		if not tmp_dir.file_path.exists():
			if log_level >= 0: loader.stop(success=False)
			extract_dir.fp.delete(forced=True)
			tmp_dir.fp.delete(forced=True)
			return r3sponse.error_response(f"Failed to install package [{package}], failed to write out {tmp_dir.file_path.path}.", log_level=log_level)

		# post installation.
		if post_install not in [None, False, ""]:
			if log_level >= 0: loader.mark(new_message=f"Executing post installation script of package {package}")
			os.system(f'chmod +x {tmp_dir.file_path.path}{post_install}')
			print(f"{syst3m.color.orange}Root permission{syst3m.color.end} required to install package {package}.")
			if log_level >= 0: loader.hold()
			os.system("sudo ls | grep ASJKBKJBkjuiyy89y23smndbKUy3hkjNMADBhje")
			if log_level >= 0: loader.release()
			output = syst3m.utils.__execute_script__(f"sudo -u {USER} bash {tmp_dir.file_path.path}{post_install} {post_install_args}")
			if "Successfully installed " in output:
				if log_level >= 0: loader.stop()
				extract_dir.fp.delete(forced=True)
				tmp_dir.fp.delete(forced=True)
				return r3sponse.success_response(f"Successfully installed package [{package}].", log_level=log_level)
			else:
				if log_level >= 0: loader.stop(success=False)
				extract_dir.fp.delete(forced=True)
				tmp_dir.fp.delete(forced=True)
				return r3sponse.error_response(f"Failed to install package [{package}], failed to run the post installation script output: \n{output}.", log_level=log_level)
		else:
			os.system(f"mv {tmp_dir.file_path.path} {library}")
			if tmp_dir.file_path.exists():
				if log_level >= 0: loader.stop()
				extract_dir.fp.delete(forced=True)
				tmp_dir.fp.delete(forced=True)
				return r3sponse.success_response(f"Successfully installed package [{package}].", log_level=log_level)
			else:
				if log_level >= 0: loader.stop(success=False)
				extract_dir.fp.delete(forced=True)
				tmp_dir.fp.delete(forced=True)
				return r3sponse.error_response(f"Failed to install package [{package}], failed to move the library to {library}.", log_level=log_level)

		#
	def uninstall(self, package, log_level=0):

		# loader.
		if log_level >= 0: loader = syst3m.console.Loader(f"Uninstalling package {package}")

		# check package.
		package = self.__package_identifier__(package)
		if package not in list(self.packages.keys()):
			if log_level >= 0: loader.stop(success=False)
			return r3sponse.error_response(f"Specified package [{package} does not exist.", log_level=log_level)

		# delete package.
		if self.packages[package]["library"] not in ["", None, False]:
			file_path = Formats.FilePath(self.packages[package]["library"])
			if file_path.exists():
				try: os.remove(file_path.path)
				except PermissionError: file_path.delete(forced=True, sudo=True)
			if file_path.exists():
				if log_level >= 0: loader.stop(success=False)
				return r3sponse.error_response(f"Failed to uninstall package [{package}].", log_level=log_level)

		# alias.
		os.system(f"rm -fr /usr/local/bin/{package}")

		# success.
		if log_level >= 0: loader.stop()
		return r3sponse.success_response(f"Successfully uninstalled package [{package}].", log_level=log_level)

		#
	def update(self, package="all", post_install_args="", log_level=0):
		# update all recursive.
		if package == "all":
			c = 0
			for package, info in self.packages.items():
				if self.__installed__(package):
					response = self.update(package, log_level=log_level)
					if response["error"] != None and "already up-to-date" not in response["error"].lower(): return response
					elif response.success: c += 1
			return r3sponse.success_response(f"Successfully updated {c} package(s).", log_level=0)
		# update package.
		else:
			# check package.
			package = self.__package_identifier__(package)
			if package not in list(self.packages.keys()):
				return r3sponse.error_response(f"Package [{package} does not exist.", log_level=log_level)
			if not self.__installed__(package):
				return r3sponse.error_response(f"Package [{package} is not installed.", log_level=log_level)
			response = self.version(package, remote=True)
			if response["error"] != None: 
				r3sponse.log(response=response, log_level=log_level)
				return response
			remote_version = response.version
			response = self.version(package, remote=False)
			if response["error"] != None: 
				r3sponse.log(response=response, log_level=log_level)
				return response
			if response.version == remote_version:
				return r3sponse.error_response(f"Package {package} is already up-to-date ({response.version}).", log_level=log_level)
			response = self.install(package, post_install_args=post_install_args, log_level=log_level)
			if response["error"] != None: return response
			return r3sponse.success_response(f"Successfully updated package [{package}].")
	def version(self, package, remote=False):
		if remote:
			version = self.packages[package]["version"]
			remote = "remote "
		else:
			remote = ""
			package = self.__package_identifier__(package)
			if package not in list(self.packages.keys()):
				return r3sponse.error_response(f"Specified package [{package} does not exist.")
			if package in ["package-manager", "package_manager"]:
				path = f'{SOURCE_PATH}/.version'
				if not os.path.exists(path):
					return r3sponse.error_response(f"Failed to retrieve the version of package {package}.")
				version = syst3m.utils.__load_file__(path).replace("\n","")
			elif self.packages[package]["library"] not in ["", False, None]:
				path = f'{self.packages[package]["library"]}/.version'
				if not os.path.exists(path):
					return r3sponse.error_response(f"Failed to retrieve the version of package {package}.")
				version = syst3m.utils.__load_file__(path).replace("\n","")
			else:
				return r3sponse.error_response(f"Failed to retrieve the version of package {package}.")
		# handler.
		return r3sponse.success_response(f"Successfully retrieved the {remote}version of package {package}.", {
			"version":version,
		})
	def up_to_date(self, package):
		self.__download_packages_info__()
		package = self.__package_identifier__(package)
		if package not in list(self.packages.keys()):
			return r3sponse.error_response(f"Package [{package} does not exist.")
		if not self.__installed__(package):
			return r3sponse.error_response(f"Package [{package} is not installed.")
		response = self.version(package, remote=True)
		if response["error"] != None: return response
		remote_version = response.version
		response = self.version(package, remote=False)
		if response["error"] != None: 
			return response
		up_to_date = response.version == remote_version
		return r3sponse.success_response(f"Successfully compared the versions of package {package}.", {
			"up_to_date":up_to_date,
			"current_version":response.version,
			"remote_version":remote_version,
		})

	# system functions.
	def __request__(self, url="/", data={}, json=True):
		def clean_url(url, strip_first=True, strip_last=True, remove_double_slash=True):
			while True:
				if strip_last and url[len(url)-1] == "/": url = url[:-1]
				elif strip_first and url[0] == "/": url = url[1:]
				elif remove_double_slash and "//" in url: url = url.replace("//","/")
				else: break
			return url
		def encode_data(data):
			return f"?{urllib.parse.urlencode(data)}"
			#

		# url.
		url = f"https://api.vandenberghinc.com/{clean_url(url)}/"
		if data != {}: url += encode_data(data)

		# request.
		response_object = requests.get(url, allow_redirects=True)
		if response_object.status_code != 200:
			return r3sponse.error_response(f"Invalid request ({url}) [{response_object.status_code}]: {response_object.text}")
		if json:
			try: response = response_object.json()
			except: return r3sponse.error_response(f"Unable to serialize output: {response_object}, text: {response_object.text}")
			return response
		return response_object

		#
	def __download_packages_info__(self):
		response = self.__request__("/packages/list/")
		if not r3sponse.success(response): raise ValueError(f"Failed to download the vandenberghinc packages, error: {response['error']}")
		self.packages = response["packages"]
	def __package_identifier__(self, package):
		return package.replace(" ","-")
		#
	def __installed__(self, package):
		if package in ["package-manager", "package_manager"]:
			return True
		elif self.packages[package]["library"] not in ["", None, False]:
			path = self.packages[package]["library"]
			while True:
				if len(path) > 0 and path[len(path)-1] == "/": path = path[:-1]
				else: break
			return os.path.exists(path)
		else:
			raise ValueError(f"Unable to determine if package {package} is installed.")

# initialized class.
package_manager = PackageManager()
