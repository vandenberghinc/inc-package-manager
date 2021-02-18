#!/usr/bin/env bash

# functions.
function osinfo() {
    user=$(echo $USER)
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        os="linux"
        group="root"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        os="macos"
        group="wheel"
    elif [[ "$OSTYPE" == "cygwin" ]]; then
       os="posix"     # POSIX compatibility layer and Linux environment emulation for Windows
       group="root"
    elif [[ "$OSTYPE" == "msys" ]]; then
        os="mysys"    # Lightweight shell and GNU utilities compiled for Windows (part of MinGW)
        group="root"
    elif [[ "$OSTYPE" == "win32" ]]; then
        os="win32"    # I'm not sure this can happen.
        group="root"
    elif [[ "$OSTYPE" == "freebsd"* ]]; then
        os="freebsd"    # ...
        group="root"
    else
        os="unknown"    # Unknown.
        group="root"
    fi
    #echo "Operating system: "$os
}
osinfo

# libs.
if [[ "$os" == "macos" ]] ; then
    a=1
elif [[ "$os" == "linux" ]] ; then
    sudo apt-get -y install git
else 
    echo "Error: unsupported operating system $OS."
    exit 1
fi

# remote install.
alias="inc-package-manager"
rm -fr /tmp/$alias
git clone https://github.com/vandenberghinc/$alias /tmp/$alias
chmod +x /tmp/$alias/$alias/requirements/installer
bash /tmp/$alias/$alias/requirements/installer
rm -fr /tmp/$alias/