import math
import sys
from scipy import constants


#ENERGY TO WAVELENGTH FORMULA
#E (eV) = 12398.42 / λ (Angstrom)

def energy_to_wavelength(energy):
	constant = (constants.speed_of_light* 1e+10)*(constants.Planck/constants.electron_volt) # in Angstrom
	wavelength = (constant) / energy
	#print('constant = {}, energy = {},final wavelength = {}'.format(constant, energy, wavelength))
	return wavelength

def wavelength_to_energy(wavelength):
	constant = (constants.speed_of_light*1e+10)*(constants.Planck/constants.electron_volt) # in Angstrom
	energy = constant / wavelength
	#print('constant = {}, wavelength = {}, final energy = {}'.format(constant, wavelength, energy))
	return energy 


class Calculator:
	"""
	Make a calculator object that can calculate resolution formulas (and nothing else)

	"""
	def __init__(self):
		self.detector_radius = None
		self.resolution = None
		self.detector_distance = None
		self.theta = 0
		self.energy = None

	def set_all_variables(self, variable_dict):
		for key in variable_dict:
			self.set_variables(key, variable_dict[key])

		

	def set_variables(self, name, value):
		
		if name == 'DetectorRadius':
			self.detector_radius = value
			if self.detector_radius == 244.7:
				self.detector_radius = 244.7/2 #in angstroms
			else:
				self.detector_radius = 164/2
			
				
		elif name == "Resolution":
			self.resolution = value

		elif name == "DetectorDistance":
			self.detector_distance = value #in angstroms
		
		elif name == 'theta':
			self.theta = value

		elif name == 'Energy':
			self.energy = value
			
	# d (resolution)
	def calcD(self, r = None, L = None, energy = None, theta = None):
		r = r or self.detector_radius
		L = L or self.detector_distance
		energy = energy or self.energy
		wavelength = energy_to_wavelength(energy)
		try:
			val1 = math.atan(r / L)
			d = wavelength / (2 * math.sin(0.5 * val1))
			other_d = wavelength / (2 * math.sin(0.5 * math.atan(r / L) + 0))
			#print('detector_radius = {}, detector_distance = {}, wavelength = {}, energy = {}, other_d = {}'.format(r, L, wavelength, energy, other_d))
			return other_d
		except Exception as e:
			return e



	# L (crystal-to-detector distance)
	def calcL(self, r = None, d = None, energy = None, theta = None):
		r = r or self.detector_radius
		d = d or self.resolution
		energy = energy or self.energy
		wavelength = energy_to_wavelength(energy)
		try:
			val1 = math.asin(wavelength / (2 * d))
			L = r / math.tan(2 * val1)
			#print('detector_radius = {}, resolution = {}, wavelength = {}, energy = {}, final detector_distance = {}'.format(r, d, wavelength, energy, L))
			return L
		except Exception as e:
			return e


	def calcTheta(self, r = None, L = None, energy = None, d = None):
		r = r or self.detector_radius
		L = L or self.detector_distance
		energy = energy or self.energy
		d = d or self.resolution
		wavelength = energy_to_wavelength(energy)
		try:
			val1 = math.asin(wavelength / (2 * d))
			val2 = math.atan(r / L)
			theta = val1 - 0.5 * val2
			return theta
		except Exception as e:
			return e


	def calcenergy(self, r = None, L = None, d = None, theta = None):
		r = r or self.detector_radius
		L = L or self.detector_distance
		d = d or self.resolution
		valin = 0.5*math.atan(r/L)
		try:
			val1 = math.atan(r / L)
			wavelength = 2 * d * math.sin(0.5 * val1)
			energy = wavelength_to_energy(wavelength)
			#print('detector_radius = {}, resolution = {}, detector_distance = {}, wavelength = {}, final energy = {}'.format(r, d, L, wavelength, energy))
			return energy
		except Exception as e:
			return e

