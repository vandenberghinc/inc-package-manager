#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# imports.
import os, sys, ast, json, glob, platform, subprocess, random, requests, urllib

# inc imports.
import syst3m
from dev0s import *

# source.
SOURCE_NAME = "inc_package_manager"
ALIAS = "inc-package-manager"
SOURCE_PATH = Defaults.source_path(__file__, back=3)
BASE = Defaults.source_path(SOURCE_PATH, back=1)
OS = Defaults.operating_system(supported=["linux", "macos"])
Defaults.alias(alias=ALIAS, executable=f"{SOURCE_PATH}")

# options.
LOG_LEVEL = Defaults.log_level(default=0)
JSON = CLI.arguments_present(["-j", "--json"])

# universal variables.
OWNER = USER = os.environ.get("USER")
GROUP = "root"
HOME = "/home/"
USER_HOME = f"/home/{USER}/"
MEDIA = f"/media/{USER}/"
if OS in ["macos"]: 
	HOME = "/Users/"
	USER_HOME = f"/Users/{USER}/"
	MEDIA = f"/Volumes/"
	GROUP = "wheel"

# database.
DATABASE = f"/etc/{ALIAS}/"
if not Files.exists(DATABASE[:-1]):
	print(f"{color.orange}Root permissions{color.end} required to create database {DATABASE}.")
	os.system(f"sudo mkdir {DATABASE} && sudo chown -R {USER}:{GROUP} {DATABASE} && sudo chmod -R 770 {DATABASE}")

