#!/usr/bin/env spack-python

import stackprinter
from tabulate import tabulate
import json
from itertools import groupby
import os
import yaml

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

def normalize_spackpkgs(pkg_lst):
    master = [] # accumulate packages here
    def spackage2module(spackage):
        hash = spackage.hash
        
    def normalize_spackpkg(pkg, master):
        newpkg = {}
        newpkg['name'] = g(pkg, 'name')

def normalize_spiderpkgs(pkg_lst):
    master = [] # accumulate packages here
    # produce a dict representing a package
    # with (at least) these keys: 'name', 'version', 'required', and 'module_name'
    def normalize_spiderpkg(pkg, master):
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
        normalize_spiderpkg(pkg, master)
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

# run spider command
def get_modules_info():
    # cmd = module_info_cmd()
    cmd = ''.join([ os.environ['LMOD_DIR'],  "/spider" ,
                    ' '.join([' -o' , 'jsonSoftwarePage', os.environ['MODULEPATH']])])
    stream = os.popen(cmd)
    output = json.loads(stream.read())
    return(output)

def get_spack_modules_conf():
    cmd = 'spack config get modules'
    stream = os.popen(cmd)
    output = yaml.load(stream.read())
    return(output)

def spack_hashlength():
    config = get_spack_modules_conf()
    return(config['modules']['default']['lmod']['hash_length'])

hash_length = spack_hashlength()

def spack_find_json(args=''):
    cmd = ' '.join(['spack',  'find', args, '--json'])
    stream = os.popen(cmd)
    output = json.loads(stream.read())
    return(output)
    

def spackage2ModName(spackage):
    modulename = '-'.join(["/".join([spackage['name'], spackage['version']]),
                           spackage['hash'][0:hash_length]])
    return(modulename)

def normalizeSpackages(list):
    master = [] # accumulate packages here
    def normalizeSpackage(spackage, master):
        # 'name', 'version', 'required', and 'module_name'
        pkg = {}
        pkg['name'] = spackage['name']
        pkg['version'] = spackage['version']
        pkg['required'] = ' '.join([ spackage['compiler']['name'], spackage['compiler']['version'] ])
        pkg['module_name'] = spackage2ModName(spackage)
        master.append(pkg)
    
    for pkg in list:
        normalizeSpackage(pkg, master)
        
    return(master)

print("output from spack:")
spackPackages = normalizeSpackages(spack_find_json())
availableSW(spackPackages)

print("output from lmod:")
spiderPackages = normalize_spiderpkgs(get_modules_info())
availableSW(spiderPackages)
