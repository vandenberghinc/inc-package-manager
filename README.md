# Inc-Package-Manager
Author(s):  Daan van den Bergh<br>
Copyright:  © 2020 Daan van den Bergh All Rights Reserved<br>
<br>
<br>
<p align="center">
  <img src="https://raw.githubusercontent.com/vandenberghinc/public-storage/master/vandenberghinc/icon/icon.png" alt="Bergh-Encryption" width="50"/>
</p>

## Installation
Open a terminal and execute the following command to install the package-manager. <br>
Short install.
	
	curl -s https://raw.githubusercontent.com/vandenberghinc/inc-package-manager/master/inc_package_manager/requirements/installer.remote | bash 

## CLI:
	Usage: package-manager <mode> <options> 
	Modes:
	    --install package-name : Install a package.
	    --uninstall package-name : Uninstall a package.
	    --update [optional: package-name] : Update all packages, optionally specify one package to update.
	    --version package-name [optional: --remote]: Retrieve the installed / remote version of a package.
	    --config : Configure the package-manager.
	       --api-key your-api-key : Specify your vandenberghinc api key.
	    -h / --help : Show the documentation.
	Author: Daan van den Bergh. 
	Copyright: © Daan van den Bergh 2020. All rights reserved.

## Python Examples.

Manage the packages through the python api.
```python

# import the package.
from inc_package_manager import package_manager

# configure your api key.
package_manager.api_key = "your-api-key"

# installing packages.
response = package_manager.install("nas-server")

# uninstalling packages.
response = package_manager.uninstall("nas-server")

# updating packages.
response = package_manager.update("nas-server")

# retrieve the installed version.
response = package_manager.version("nas-server")

# retrieve the remote version.
response = package_manager.version("nas-server", remote=True)

# handling the response.
if response.success: 
	print(response.message)
	print(f"Version: {response.version}")
else:
	print(f"Error: {response.error}")

# some response functions.
response.items()
response.keys()
response.dict()

```
