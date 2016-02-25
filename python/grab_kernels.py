import numpy as np
import matplotlib.pyplot as plt
from kernels import Kernels

years = [ 2005 ]
months = np.arange(1,13)
QA_OK = np.array([8, 72, 136, 200, 1032, 1288, 2056, 2120, 2184,  2248])

for year in years:
    nsamples = 0
    for month in months:
        fname = "MODIS_BRDF/hainich_%04d_%02d.txt" % ( year, month )
        reflt = np.loadtxt ( fname, delimiter=";", usecols=np.arange(15,22) )/10000.
        nsamples += reflt.shape[0]
    
    doys = np.empty ( nsamples )
    qa = np.empty ( nsamples )
    qa_pass = np.empty ( nsamples )
    refl = np.empty ( (nsamples,7) )
    angs = np.empty ( (nsamples,4) )
    istart = 0
    for month in months:
        print "->%d, %d<-" % ( year, month )
        fname = "MODIS_BRDF/hainich_%04d_%02d.txt" % ( year, month )
        doyt = np.loadtxt ( fname, delimiter=";", usecols=[2] ) - year*1000
        n = len(doyt)
        doys[istart:(istart+n)] = doyt
        reflt = np.loadtxt ( fname, delimiter=";", usecols=np.arange(15,22) )/10000.
        refl[istart:(istart+n),:] = reflt
        angst = np.loadtxt ( fname, delimiter=";", usecols=np.arange (11,15))/100.
        angs[istart:(istart+n), :] = angst
        #angs are sza,vza,saa,vaa
        qa1kt = np.loadtxt ( fname, delimiter=";", usecols=[10] )
        qa[istart:(istart+n)] = qa1kt

        qa_passt = np.logical_or.reduce([qa1kt == x for x in QA_OK ])
        qa_passt = qa_passt.astype(np.int8)
        qa_pass[istart:(istart+n)] = qa_passt
        istart = istart + n
        #K_obs =  Kernels( angs[:,1], angs[:,0], angs[:,2] - angs[:,3], \
            #LiType='Sparse', doIntegrals=False, \
            #normalise=1, RecipFlag=True, RossHS=False, MODISSPARSE=True, \
            #RossType='Thick' )
qa_pass = qa_pass.astype ( np.bool )
K_obs =  Kernels(angs[:,1], angs[:,0], angs[:,2] - angs[:,3], \
        LiType='Sparse', doIntegrals=False, \
        normalise=1, RecipFlag=True, RossHS=False, MODISSPARSE=True, \
        RossType='Thick' )

kern = np.ones (( doys.shape[0], 3 )) # Store the kernels in an array
kern[ :, 1 ] = K_obs.Ross
kern[ :, 2 ] = K_obs.Li

for doy_win in np.arange ( 0,366,16 ):
    doy_pass = np.logical_and ( doys >= doy_win, doys < ( doy_win + 16 ) )
    doy_pass = doy_pass * qa_pass
    if doy_pass.sum() < 7:
        print "Skipping period starting in %d" % doy_win
        continue
    K = kern[ doy_pass, :]
    for band in xrange (7):
        obs = refl[ doy_pass, band]
        (f, rmse, rank, svals ) = np.linalg.lstsq( K, obs )
        print "\t%d Period starting %d. Kernels:" % (band, doy_win), f, "RMSE: %f" % rmse
    break