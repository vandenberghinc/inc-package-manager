#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# imports.
from inc_package_manager.classes import *

# source path & version.
from dev0s.shortcuts import Version, Directory, Files, gfp
source = Directory(gfp.base(__file__))
base = Directory(source.fp.base())
version = Version(Files.load(source.join(".version")))