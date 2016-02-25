
from math import sqrt

# Convert narrow to braodband based on specific coefficients for every narrow band +/- a constant
def NarrowToBroadband(coefficients, NarrowBandReflectances, BroadbandAlbedo):
	for band_number in range(1, 8):
		BroadbandAlbedo[:,:] = BroadbandAlbedo[:,:] + \
                 (coefficients[band_number] * NarrowBandReflectances[:,:,band_number-1])

	BroadbandAlbedo[:,:] = BroadbandAlbedo[:,:] + coefficients['c']

	return BroadbandAlbedo

def GetUncertaintyNarrowToBroadbandConversion(coefficients, RSE_from_BB_conversion):
	#Land surface reflectance one standard deviation noise estimates
	#From Roy D.P., Jin Y., Lewis P.E., Justice C.O. (2005)
	#  Prototyping a global algorithm for systematic fire-affected
	#  area mapping using MODIS time series data
	#  Remote Sensing of Environment 97 (2005) 137-162
	surface_reflectance_SD_noise_estimates = {1:0.004, 2:0.015, 3:0.003, 4:0.004, 5:0.013, 6:0.010, 7:0.006 }
	denominator = 0.0

	uncertainty = RSE_from_BB_conversion ** 2

	for band_number in range(1, 8):
		uncertainty = uncertainty + \ 
          ( coefficients[band_number] * surface_reflectance_SD_noise_estimates[band_number]**2 )

		denominator = denominator + coefficients[band_number] 

	uncertainty = sqrt(uncertainty / denominator)

	return uncertainty

#---------------------Shortwave--------------------#
rse_bb_short = 0.0078
bb_short = numpy.zeros((ymax, xmax), numpy.float32 )
#short = 0.160*b1 + 0.291*b2 + 0.243*b3 + 0.116*b4 + 0.112*b5 + 0.081*b7 - 0.0015
coeff_bb_short = {1:0.160, 2:0.291, 3:0.243, 4:0.116, 5:0.112, 6:0.0, 7:0.081, 'c':-0.0015}
bb_short = NarrowToBroadband(coeff_bb_short, reflectance, bb_short)

uncertainty_bb_short = numpy.zeros((ymax, xmax), numpy.float32 )
uncertainty_bb_short[:,:] = GetUncertaintyNarrowToBroadbandConversion(coeff_bb_short, rse_bb_short)

#--------------------- Visible ----------------------#
rse_bb_visible = 0.0017
bb_visible = numpy.zeros((ymax, xmax), numpy.float32 )
#visible = 0.331*b1 + 0.424*b3 + 0.246*b4
coeff_bb_visible = {1:0.331, 2:0.0, 3:0.424, 4:0.246, 5:0.0, 6:0.0, 7:0.0, 'c':0.0}
bb_visible = NarrowToBroadband(coeff_bb_visible, reflectance, bb_visible)

uncertainty_bb_visible = numpy.zeros((ymax, xmax), numpy.float32 )
uncertainty_bb_visible[:,:] = GetUncertaintyNarrowToBroadbandConversion(coeff_bb_visible, rse_bb_visible)

rse_bb_diffuse_visible = 0.0052
bb_diffuse_visible = numpy.zeros((ymax, xmax), numpy.float32 )
#diffuse_visible = 0.246*b1 + 0.528*b3 + 0.226*b4 - 0.0013
coeff_bb_diffuse_visible = {1:0.246, 2:0.0, 3:0.528, 4:0.226, 5:0.0, 6:0.0, 7:0.0, 'c':-0.0013}
bb_diffuse_visible = NarrowToBroadband(coeff_bb_diffuse_visible, reflectance, bb_diffuse_visible)

rse_bb_direct_visible = 0.0028
bb_direct_visible = numpy.zeros((ymax, xmax), numpy.float32 )
#direct_visible = 0.369*b1 + 0.374*b3 + 0.257*b4
coeff_bb_direct_visible = {1:0.369, 2:0.0, 3:0.374, 4:0.257, 5:0.0, 6:0.0, 7:0.0, 'c':0.0}
bb_direct_visible = NarrowToBroadband(coeff_bb_direct_visible, reflectance, bb_direct_visible)

# --------------------- NIR ---------------------#
rse_bb_NIR = 0.005
bb_NIR = numpy.zeros((ymax, xmax), numpy.float32 )
#NIR = 0.039*b1 + 0.504*b2 - 0.071*b3 + 0.105*b4 + 0.252*b5 + 0.069*b6 + 0.101*b7
coeff_bb_NIR = {1:0.039, 2:0.504, 3:-0.071, 4:0.105, 5:0.252, 6:0.069, 7:0.101, 'c':0.0}
bb_NIR = NarrowToBroadband(coeff_bb_NIR, reflectance, bb_NIR)

uncertainty_bb_NIR = numpy.zeros((ymax, xmax), numpy.float32 )
uncertainty_bb_NIR[:,:] = GetUncertaintyNarrowToBroadbandConversion(coeff_bb_NIR, rse_bb_NIR)

rse_bb_diffuse_NIR = 0.008
bb_diffuse_NIR = numpy.zeros((ymax, xmax), numpy.float32 )
#bb_diffuse_NIR = 0.085*b1 + 0.693*b2 - 0.146*b3 + 0.176*b4 + 0.146*b5 + 0.043*b7 - 0.0021
coeff_bb_diffuse_NIR = {1:0.085, 2:0.693, 3:-0.146, 4:0.176, 5:0.146, 6:0.0, 7:0.043, 'c':-0.0021}
bb_diffuse_NIR = NarrowToBroadband(coeff_bb_diffuse_NIR, reflectance, bb_diffuse_NIR)

rse_bb_direct_NIR = 0.0062
bb_direct_NIR = numpy.zeros((ymax, xmax), numpy.float32 )
#bb_direct_NIR = 0.037*b1 + 0.479*b2 - 0.068*b3 + 0.0976*b4 + 0.266*b5 + 0.0757*b6 + 0.107*b7
coeff_bb_direct_NIR = {1:0.037, 2:0.479, 3:-0.068, 4:0.0976, 5:0.266, 6:0.0757, 7:0.107, 'c':0.0}
bb_direct_NIR = NarrowToBroadband(coeff_bb_direct_NIR, reflectance, bb_direct_NIR)

