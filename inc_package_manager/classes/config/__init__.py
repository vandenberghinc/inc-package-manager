#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# imports.
import os, sys, ast, json, glob, platform, subprocess, random, requests, urllib

# inc imports.
import cl1, syst3m
from fil3s import Files, Formats
from r3sponse import r3sponse

# source.
SOURCE_NAME = "inc_package_manager"
ALIAS = "inc-package-manager"
SOURCE_PATH = syst3m.defaults.source_path(__file__, back=3)
BASE = syst3m.defaults.source_path(SOURCE_PATH, back=1)
OS = syst3m.defaults.operating_system(supported=["linux", "osx"])
syst3m.defaults.alias(alias=ALIAS, executable=f"{SOURCE_PATH}")

# universal variables.
OWNER = USER = os.environ.get("USER")
GROUP = "root"
HOME = "/home/"
USER_HOME = f"/home/{USER}/"
MEDIA = f"/media/{USER}/"
if OS in ["osx"]: 
	HOME = "/Users/"
	USER_HOME = f"/Users/{USER}/"
	MEDIA = f"/Volumes/"
	GROUP = "wheel"

# database.
DATABASE = f"/etc/{ALIAS}/"
if not os.path.exists(DATABASE[:-1]):
	print(f"{syst3m.color.orange}Root permissions{syst3m.color.end} required to create database {DATABASE}.")
	os.system(f"sudo mkdir {DATABASE} && sudo chown -R {USER}:{GROUP} {DATABASE} && sudo chmod -R 770 {DATABASE}")

