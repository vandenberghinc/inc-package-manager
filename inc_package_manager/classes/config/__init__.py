#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# imports.
import os, sys, ast, json, glob, platform, subprocess, random, requests, urllib

# inc imports.
import dev0s, syst3m
from dev0s import *

# source.
ALIAS = "inc-package-manager"

# checks.
SOURCE = Directory(Defaults.source_path(__file__, back=3))
OS = Defaults.operating_system(supported=["linux", "macos"])
Defaults.alias(alias=ALIAS, executable=f"{SOURCE}")

# database.
DATABASE = Directory(f"/etc/{ALIAS}/")
if not Files.exists(str(DATABASE)[:-1]):
	print(f"{color.orange}Root permissions{color.end} required to create database {DATABASE}.")
	os.system(f"sudo mkdir {DATABASE} && sudo chown -R {Defaults.vars.user}:{Defaults.vars.group} {DATABASE} && sudo chmod -R 770 {DATABASE}")

