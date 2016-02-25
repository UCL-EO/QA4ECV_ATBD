#!/usr/bin/env python
import numpy as np
import scipy
import pylab as plt
import numpy.ma as ma
import datetime
import glob
from netCDF4 import Dataset
import os
# easy_install spectral
import spectral.io.envi as envi


def ensure_dir(f): 
    # maybe its a filename
    try:
        fd = os.path.dirname(f)
        if not os.path.exists(fd):
            os.makedirs(fd)
        return True
    except:
        pass
    
    try:
        if not os.path.exists(f):
            os.makedirs(f)
        return True
    except:
        return False
    
def doy2date(doys,baseyear=1998):
    # convert doys list to date field
    year = baseyear
    return np.array([datetime.datetime(year, 1, 1) + datetime.timedelta(doy - 1) \
                   for doy in doys])

def date2doy(dates,baseyear=1998):
    # convert date field to doys list
    base = datetime.datetime(baseyear, 1, 1)
    try:
        return (dates-base).days
    except:
        return np.array([(datef-base).days \
                   for datef in dates])
    
def readwriteFile(f_file,\
             ofile='/tmp/test.nc',baseyear=1998,sensor='none',\
             verbose=False,dtype=None,ofile_type='envi'):
    '''
    Sort formatting of file
    '''

    if not ensure_dir(ofile): return None,None
    fileroot = '.'.join(ofile.split('.')[:-1])  
    if ofile_type == 'envi':
      ofile = fileroot + '.hdr'
      ofile2 = fileroot + '.img'
    else:
      ofile2 = ofile

    if verbose:
        print f_file,'\n\t--->>>',ofile
   
    rootgrp = Dataset(f_file,'r')
    datasets = rootgrp.variables.keys()
    nx = len(rootgrp.dimensions['x'])
    ny = len(rootgrp.dimensions['y'])
    nt = len(datasets)
 
    if dtype is not None:
      # need to check if already done
      if os.path.isfile(ofile2): 
        statinfo = os.stat(ofile2)
        if statinfo.st_size == 4 * nx * ny * nt:
          return

    # try to delete file first (some issue with the library)
    try:
        os.remove(ofile)
        if ofile_type == 'envi': 
          os.remove(ofile2)
    except:
        pass

    time = np.zeros(nt)

    # time field
    for i in xrange(len(datasets)):
      field = datasets[i].split('_')[-2]
      try:
        year = int(field[:4])
        doy = int(field[4:])
        thisdate = datetime.datetime(year, 1, 1) + datetime.timedelta(doy - 1)
      except:
        year = baseyear
        doy = int(field[4:])
        thisdate = datetime.datetime(year, 1, 1) + datetime.timedelta(doy - 1)
      # days from base year Jan 1
      # time field
      time[i] = date2doy(thisdate)


    if ofile_type == 'nc':    
      ncfile = Dataset(ofile,mode='w',clobber=True,diskless=False,persist=False,format='NETCDF4')
      ncfile.createDimension('time',nt)
      ncfile.createDimension('x',nx)
      ncfile.createDimension('y',ny)
    
      timer = ncfile.createVariable('time',np.dtype('float32').char,('time',))
      x = ncfile.createVariable('x',np.dtype('float32').char,('x',))
      y = ncfile.createVariable('y',np.dtype('float32').char,('y',))
      x.units = '1 km'
      y.units = '1 km'
      timer.units = 'days from 1 1 %d' % baseyear
      timer[:] = time[:]
      result = ncfile.createVariable('data',np.dtype('float32').char,('time','x','y'))

      for i in xrange(len(datasets)):
        if dtype is None:
          result[i,:,:] = rootgrp.variables[datasets[i]][:]
        elif dtype == 'sd':
          sd = rootgrp.variables[datasets[i]][:]
          mask = ~(sd == 0)
          weight = np.zeros_like(sd)
          weight[mask] = 1./(sd[mask]*sd[mask])
          result[i,:,:] = weight
        elif  dtype == 'var':
          var = rootgrp.variables[datasets[i]][:]
          mask = ~(var == 0)
          weight = np.zeros_like(var)
          weight[mask] = 1./(var[mask])
          result[i,:,:] = weight

    else:
      meta = {'lines':ny,'samples':nx,'bands':nt,'time':time,'baseyear':baseyear,'sensor':sensor} 
      # flat binary file - envi format
      img = envi.create_image(ofile,metadata=meta,dtype='float32',interleave='bip')
      result = img.open_memmap(writable=True)
      resultip = np.zeros(result.shape)

      for i in xrange(len(datasets)):
        if dtype is None:
          resultip[:,:,i] = rootgrp.variables[datasets[i]][:]
        elif dtype == 'sd':
          sd = rootgrp.variables[datasets[i]][:]
          mask = ~(sd == 0)
          weight = np.zeros_like(sd)
          weight[mask] = 1./(sd[mask]*sd[mask])
          resultip[:,:,i] = weight
        elif  dtype == 'var':
          var = rootgrp.variables[datasets[i]][:]
          mask = ~(var == 0)
          weight = np.zeros_like(var)
          weight[mask] = 1./(var[mask])
          resultip[:,:,i] = weight
      if verbose:print '\tcopying data ...'
      result[:] = resultip[:]

    if ofile_type == 'nc':
      ncfile.close()      
      rootgrp.close()
    else:
      if verbose:print '\tclosing file ...'
      del img,result,resultip
    

def trysd(f_file,\
          ofile_type='envi',\
          ofile='/tmp/test.nc', baseyear=1998,\
          verbose=False, sensor='none'):
    '''
    Check to see if file is sd or var and if so, convert to a weigfht file
    '''
    # check filename
    for sd in ['sig_','SD:']:
      #import pdb;pdb.set_trace()
      if f_file.count(sd):
        readwriteFile(f_file,\
                    sensor=sensor,\
                    ofile=ofile.replace(sd,'weight'+sd[-1]),\
                    baseyear=baseyear,verbose=verbose,\
                    dtype='sd',ofile_type=ofile_type)
      elif f_file.count('VAR'):
        readwriteFile(f_file,\
                    sensor=sensor,\
                    ofile=ofile.replace('VAR','weight'),\
                    baseyear=baseyear,verbose=verbose,\
                    dtype='var',ofile_type=ofile_type)


# make output directory
odir = 'inputs'
ensure_dir(odir)
ofile_type = 'envi'
# convert all files
tiles = ['h18v04', 'h19v08', 'h22v02', 'h25v06']
tiles = ['h18v03']
for sensor in ['meris', 'vgt']:
    for tile in tiles:
        # MvL: the list iterated on the following line may need modifying depending on...
        # ...the actual format of files supplied. E.g. 'sig_BB' may need to be 'weight'
        for dd in ['BB_','Kvol_BRDF','Kgeo_BRDF','sig_BB','snow_mask']:
            print dd
            for f in glob.glob('data/bbdr.{sensor}/{tile}*/{dd}*/*.nc'\
			.format(dd=dd,tile=tile,sensor=sensor)):
                print f
                filename = os.path.basename(f).split('.')
                print dd,f
                if filename[0] == 'bbdr':
                    sensor = filename[1]
                else:
                    sensor = filename[0]
                fn = os.path.join(odir,os.path.basename(f))
                done = False
                if ofile_type == 'envi':
                    fn = '.'.join(fn.split('.')[:-1]) + '.img'
                try:
                    if os.path.isfile(fn):
                        statinfo = os.stat(fn)
                        if statinfo.st_size > 0:
                            done = True
                            print 'Done:',f,'\n\t-->',fn
                except:
                    pass 
                if not done:
                    try:
                        readwriteFile(f,sensor=sensor,ofile=fn,ofile_type=ofile_type,baseyear=1998,verbose=True)
                    except:
                        print 'Fail:',f,'\n\t-->',fn
                # convert sd and VAR to weight
                trysd(f,ofile=fn,sensor=sensor,ofile_type=ofile_type,baseyear=1998,verbose=True)
                #os.remove(f)


# a second round for ga.brdf
odir = 'inputs'
ensure_dir(odir)
ofile_type = 'envi'
for sensor in ['ga.brdf']:
    for sensorsub in ['ga.brdf.Snow', 'ga.brdf.NoSnow', 'ga.brdf.merge']:
        print "***", sensorsub
        for tile in ['h18v04', 'h19v08', 'h22v02', 'h25v06']:
            for dd in ['mean_', 'VAR_', 'lat', 'lon', 'Entropy', 'Goodness_of_Fit', 'Relative_Entropy', 'Time_to_the_Closest_Sample', 'Weighted_Number_of_Samples']:
                for f in glob.glob('data/{sensor}/{sensorsub}/{tile}*/{dd}*/*.nc'\
			.format(dd=dd, tile=tile, sensor=sensor, sensorsub=sensorsub)):
                    filename = os.path.basename(f).split('.')
                    print '@', sensor, sensorsub, tile, dd,f
                    fn = os.path.join(odir,os.path.basename(f))
                    done = False
                    if ofile_type == 'envi':
                        fn = '.'.join(fn.split('.')[:-1]) + '.img'
                    try:
                        if os.path.isfile(fn):
                            statinfo = os.stat(fn)
                            if statinfo.st_size > 0:
                                done = True
                                print 'Done:',f,'\n\t-->',fn
                    except:
                        pass
                    print done
                    if not done:
                        try:
                            print '**Doing:', f
                            readwriteFile(f,sensor=sensor,ofile=fn,ofile_type=ofile_type,baseyear=1998,verbose=True)
                        except:
                            print 'Fail:',f,'\n\t-->',fn
                    # convert sd and VAR to weight
                    trysd(f,ofile=fn,sensor=sensor,ofile_type=ofile_type,baseyear=1998,verbose=True)
                    #os.remove(f)


# a third round for prior
odir = 'inputs'
ensure_dir(odir)
ofile_type = 'envi'
for sensor in ['prior']:
    for sensorsub in ['prior.v2.snow', 'prior.v2.nosnow', 'prior.v2.snownosnow']:
        for tile in ['h18v03']:
            for dd in ['MEAN', 'SD', 'Weighted_number_of_samples', 'land_mask']:
                for f in glob.glob('data/{sensor}/{sensorsub}/{tile}*/{dd}*/*.nc'\
			.format(dd=dd, tile=tile, sensor=sensor, sensorsub=sensorsub)):
                    filename = os.path.basename(f).split('.')
                    print sensor, sensorsub, tile, dd,f
                    fn = os.path.join(odir,os.path.basename(f))
                    done = False
                    if ofile_type == 'envi':
                        fn = '.'.join(fn.split('.')[:-1]) + '.img'
                        try:
                            if os.path.isfile(fn):
                                statinfo = os.stat(fn)
                                if statinfo.st_size > 0:
                                    done = True
                                    print 'Done:',f,'\n\t-->',fn
                        except:
                            pass 
                        if not done:
                            try:
                                readwriteFile(f,sensor=sensor,ofile=fn,ofile_type=ofile_type,baseyear=1998,verbose=True)
                            except:
                                print 'Fail:',f,'\n\t-->',fn
                        # convert sd and VAR to weight
                        trysd(f,ofile=fn,sensor=sensor,ofile_type=ofile_type,baseyear=1998,verbose=True)
                        #os.remove(f)
