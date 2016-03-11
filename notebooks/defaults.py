import sys
import os

# where is the python directory? one of these probably
for pp in ['.','python','../python','../../python']:
  try:
    ppp = os.path.abspath(pp)
    sys.path.insert(1,ppp)
  except:
    pass
# add the python directory 
import pylab as plt
import numpy as np
from glob import glob
import pandas as pd
import netCDF4
from netCDF4 import Dataset
import urllib2
from HTMLParser import HTMLParser
import os
import pickle
import kernels
import datetime
from datetime import date,timedelta
import scipy.sparse
import scipy.stats


def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)
        
def save_obj(obj, name ):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

def load_obj(name ):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)
    
scale = 1.0
datadir = os.path.abspath('../data')
print 'data directory',datadir


'''
Codes to pull netcdf files from the server

'''
# create a subclass and override the handler methods
class MyHTMLParser(HTMLParser):
    # see https://docs.python.org/2/library/htmlparser.html
    def handle_starttag(self, tag, attrs):
        pass;
        #print "Encountered a start tag:", tag
    def handle_endtag(self, tag):
        pass
        #print "Encountered an end tag :", tag
    def handle_data(self, data):
        data = data.strip()
        if len(data) and data[-1] == '/':
            # is it a directory?
            try:
                self.datadirs.append(data)
            except:
                self.datadirs = [data]
        if len(data) and data.split('.')[-1] == 'nc':
            # is it a nc file?
            try:
                self.ncfiles.append(data)
            except:
                self.ncfiles = [data]            
        
def getdirs(db):
    # get directories from url
    response = urllib2.urlopen(db,None,120)
    
    parser = MyHTMLParser()
    html = response.read()
    del response
    parser.feed(html)
    return parser

def nc_urls(db):
    '''
    obtain full list of data urls of nc files
    '''
    ncfiles = {}
    parser = getdirs(db)
    for sensor in parser.datadirs:
        ncfiles[sensor] = []
        parser2 = getdirs(db+sensor)
        if hasattr(parser2, 'datadirs'):
            for sub0 in parser2.datadirs:
                parser3 = getdirs(db+sensor+sub0)
                if hasattr(parser3, 'datadirs'):
                    for sub1 in parser3.datadirs:
                        parser4 = getdirs(db+sensor+sub0+sub1)
                        if hasattr(parser4, 'datadirs'):
                            print 'deepest level checked'
                        if hasattr(parser4, 'ncfiles'):
                            for nc in parser4.ncfiles:
                                ncfiles[sensor].append(db+sensor+sub0+sub1+nc)
                if hasattr(parser3, 'ncfiles'):
                    for nc in parser3.ncfiles:
                            ncfiles[sensor].append(db+sensor+sub0+nc)
        if hasattr(parser2, 'ncfiles'):
            for nc in parser2.ncfiles:
                ncfiles[sensor].append(db+sensor+nc)
    return ncfiles

def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)
        
def obtain_data(db,doit=True):
    print 'connecting to',db
    ncfiles = nc_urls(db)
    print 'got urls'
    nclocals = {}
    datakeys = ncfiles.keys()
    for k in datakeys:
        print k
        ensure_dir(k)
        nclocals[k] = []
        for ncfile in ncfiles[k]:
            print '.',
            if doit:
                data = urllib2.urlopen(ncfile).read()
            local = ncfile.split('/')[-1]
            nclocals[k].append(local)
            # write
            if doit:
                f = open(k+local,'wb')
                f.write(data)
                f.close()
    for k in nclocals.keys():
        if k[-1] == '/':
            nclocals[k.strip('/')] = nclocals[k]
            del nclocals[k]
    return nclocals

