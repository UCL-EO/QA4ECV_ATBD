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

