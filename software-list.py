#!/usr/bin/env spack-python

import stackprinter
from tabulate import tabulate
import json
from itertools import groupby
import os

def g(thing, attr, default=[]):
    x = default
    try:
        x = thing[attr]
    except KeyError:
        x = x
    return(x)
  
def name(thing):
    return(g(thing, 'name'))

def version(thing):
    return(g(thing, 'version'))

def module(thing):
    return(g(thing, 'module_name'))

def normalize_pkgs(pkg_lst):
    master = [] # accumulate packages here
    # produce a dict representing a package
    # with (at least) these keys: 'name', 'version', 'required', and 'module_name'
    def normalize_pkg(pkg, master):
        newpkg = {}
        newpkg['name'] = g(pkg, 'package')
        if 'versionName' in g(pkg, 'versions')[0]:
            newpkg['version'] = pkg['versions'][0]['versionName']
            if 'parent' in pkg['versions'][0]:
                newpkg['required'] = pkg['versions'][0]['parent'][0][0]
            else:
                newpkg['required'] = '<None>'
            if 'versionName' in pkg['versions'][0]:
                newpkg['version'] = pkg['versions'][0]['versionName']
                newpkg['module_name'] = pkg['versions'][0]['full']
            master.append(newpkg)
    for pkg in pkg_lst:
        normalize_pkg(pkg, master)
    return(master)

def info(item):
    return([name(item), version(item), module(item)])

def print_item(item):
    print(" ".join(info(item)))

def availableSW(table):
    srtTable = sorted(table, key=lambda x: g(x, 'required'))
    TableHeaders = {'name': 'Software Name:',
                    'version': 'Version:',
                    'required': 'Prereq. modules:',
                    'module_name': 'Module Name:'}
    print(tabulate(srtTable, headers=TableHeaders))

def module_info_cmd():
    cmmd = ''.join([ os.environ['LMOD_DIR'],  "/spider" ,
                    ' '.join([' -o' , 'jsonSoftwarePage', os.environ['MODULEPATH']])])
    return(cmmd)

# run spider command
def get_modules_info():
    cmd = module_info_cmd()
    stream = os.popen(cmd)
    output = json.loads(stream.read())
    return(output)

packages = normalize_pkgs(get_modules_info())
availableSW(packages)
