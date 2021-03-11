#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# imports.
import os, sys, ast, json, glob, platform, subprocess, random, requests, urllib

# inc imports.
from dev0s.shortcuts import *

# source.
ALIAS = "inc-package-manager"

# checks.
SOURCE = Directory(dev0s.defaults.source_path(__file__, back=3))
OS = dev0s.defaults.operating_system(supported=["linux", "macos"])
dev0s.defaults.alias(alias=ALIAS, executable=f"{SOURCE}")

# database.
DATABASE = Directory(f"/etc/{ALIAS}/")
if not Files.exists(str(DATABASE)[:-1]):
	print(f"{color.orange}Root permissions{color.end} required to create database {DATABASE}.")
	os.system(f"sudo mkdir {DATABASE} && sudo chown -R {dev0s.defaults.vars.user}:{dev0s.defaults.vars.group} {DATABASE} && sudo chmod -R 770 {DATABASE}")

