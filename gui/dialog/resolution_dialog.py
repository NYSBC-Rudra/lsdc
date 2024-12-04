from qtpy.QtWidgets import * 
from qtpy import QtCore
from qtpy import QtGui
from qtpy import QtWidgets
from qtpy.QtCore import * 
from qtpy.QtGui import * 
import sys
from gui.dialog import Calculator
import typing
import re

if typing.TYPE_CHECKING:
    from lsdcGui import ControlMain

WINDOW_SIZE = 480

#main qtpy window the calculator exists in





class CalculatorWindow(QtWidgets.QDialog):
	def __init__(self, parent: "ControlMain"):
		super(CalculatorWindow, self).__init__(parent)
		self.setFixedSize(WINDOW_SIZE,WINDOW_SIZE)
		#making radio buttons to choose formula
		self.buttonDictionary = {'DetectorDistance': {'picker' : QRadioButton('Caluclate crystal to detector distance (mm)')},
			   'Resolution': {'picker': QRadioButton("Calculate resolution Å")} , 
			#    'theta': {'picker':QRadioButton("Calculate detector 2theta")},
			   'Energy': {'picker':QRadioButton("Calculate Energy eV")},
			     'DetectorRadius':{'value':None}}
		
		#making lines to hold inputs 
		# self.r_value_enter = QComboBox()
		# self.r_value_enter.setToolTip("Choose your detector")
		# detectorList = ['NYX-Beamline (200.0mm)?', 'Dectris EIGER2 X 9M (244.7mm)']
		# self.r_value_enter.addItems(detectorList)
		# self.buttonDictionary['DetectorRadius']['value'] = self.r_value_enter
		# self.r_value_enter.setCurrentIndex(1)
		self.detectorradius_value_enter = QComboBox()
		self.detectorradius_value_enter.addItems(['244.7mm (AMX & NYX)', '164mm (FMX)'])
		self.detectorradius_value_enter.setPlaceholderText('Set detector radius')
		self.buttonDictionary['DetectorRadius']['value'] = self.detectorradius_value_enter
		#self.r_value_enter.setValidator(QDoubleValidator())



		#setting inputs to Double only

		self.detectordistance_value_enter = QLineEdit()
		self.detectordistance_value_enter.setPlaceholderText('Set crystal to detector distance')
		self.buttonDictionary['DetectorDistance']['value'] = self.detectordistance_value_enter
		self.detectordistance_value_enter.setValidator(QDoubleValidator())

		self.resolution_value_enter = QLineEdit()
		self.resolution_value_enter.setPlaceholderText('Set resolution')
		self.buttonDictionary['Resolution']['value'] = self.resolution_value_enter
		self.resolution_value_enter.setValidator(QDoubleValidator())

		#self.theta_value_enter = QLineEdit()
		# self.theta_value_enter.setPlaceholderText('Set detector theta value')
		# self.buttonDictionary['theta']['value'] = self.theta_value_enter
		#self.theta_value_enter.setValidator(QDoubleValidator())

		self.energy_value_enter = QLineEdit()
		self.energy_value_enter.setPlaceholderText('Set energy value')
		self.buttonDictionary['Energy']['value'] = self.energy_value_enter
		self.energy_value_enter.setValidator(QDoubleValidator())


		self.final_button = QPushButton('Calculate', self)
		self.final_button.clicked.connect(self.calculateValue)

		self.bottom_text = QLabel()
		self.bottom_text.setText('Enter values and Press button to calculate')


		#creating calculator object
		self.calculator = Calculator()



		layout = QVBoxLayout()
		layout.addWidget(self.detectorradius_value_enter)
		for key in self.buttonDictionary:
			if 'picker' in self.buttonDictionary[key].keys(): 
				layout.addWidget(self.buttonDictionary[key]['picker'])
			layout.addWidget(self.buttonDictionary[key]['value'])
		layout.addWidget(self.final_button)
		layout.addWidget(self.bottom_text)
		self.setLayout(layout)
		#self._createDisplay()



	# def _createButtons(self):
	# 	buttonsLayout = QGridLayout()
	# 	self.formula_picker = QRadioButton('Formula')
	# 	self.b2 = QRadioButton("Button2")

	'''
	calls resolution calculator to calculate value depending on inputs from widgets

	-outputs
		-value_to_return = value from formula calculated if no problems
		-returns nothing if a problem occured, changes bottom_text
	'''

	def calculateValue(self):
		checked_key = None
		#checking which formula to use
		for key in self.buttonDictionary:
			if key != 'DetectorRadius' and self.buttonDictionary[key]['picker'].isChecked():
				checked_key = key
		if checked_key == None:
			self.bottom_text.setText("No calculation specified (press one of the radio buttons)")
			return
		


		detectorradius_value = self.detectorradius_value_enter.currentText()
    	# checking if value is a number string or empty string
		if detectorradius_value == "" or detectorradius_value[0].isalpha() == True:
			self.bottom_text.setText("formula to calculate {} requires r value".format(checked_key))
			return


		detectorradius_value = convertDetectorRadius(detectorradius_value)



		#getting values from textboxes r_value text box
# 		r_value = self.r_value_enter.currentIndex()
# 		convertValues = [200,244.7]
# 		# print("r value = {}".format(r_value))
# 		#checking if value is a number string or empty string
# 		r_value = convertValues[r_value]
# 		r_value = float(r_value)



		resolution_value = self.resolution_value_enter.displayText()
		#checking if value is string or none if not calculating that value (trying to use .isalpha but not when value is None)
		if ((resolution_value == "" or resolution_value[0].isalpha() == True) and checked_key != 'Resolution') :
			self.bottom_text.setText("formula to calculate {} requires d value".format(checked_key))
			return

		detectordistance_value = self.detectordistance_value_enter.displayText()
		if ((detectordistance_value == "" or detectordistance_value[0].isalpha() == True) and checked_key != "DetectorDistance"):
			self.bottom_text.setText("formula to calculate {} requires L value".format(checked_key))
			return
		elif detectordistance_value != '' and checked_key != "DetectorDistance":
			if float(detectordistance_value) < 140 or float(detectordistance_value) > 350:
				self.bottom_text.setText("detector to crystal distance must be between 140 and 350mm")	
				return




		# theta_value = self.theta_value_enter.displayText()
		#if ((theta_value == "" or theta_value[0].isalpha() == True)and checked_key != 'theta'):
			# self.bottom_text.setText("formula to calculate {} requires theta value".format(checked_key))
		#	return

		energy_value = self.energy_value_enter.displayText()
		if ((energy_value == "" or energy_value[0].isalpha() == True) and checked_key != 'Energy'):
			self.bottom_text.setText("formula to calculate {} requires the energy".format(checked_key))
			return


		#setting value to return if want value returned
		value_to_return = None

		if checked_key == 'Resolution':
			detectordistance_value = float(self.detectordistance_value_enter.displayText())
			# theta_value = float(self.theta_value_enter.displayText())
			energy_value = float(self.energy_value_enter.displayText())





			variableDict = {'DetectorDistance':detectordistance_value, 
				   #'theta': theta_value, 
				   'Energy': energy_value, 'DetectorRadius': detectorradius_value}


			self.calculator.set_all_variables(variableDict)
			resolution_value = self.calculator.calcD()
			value_to_return = resolution_value
			self.resolution_value_enter.setText(str(resolution_value))
			self.calculator.set_variables('Resolution', resolution_value)
			checked_key = 'Resolution'




		elif checked_key == "DetectorDistance":

			resolution_value = float(self.resolution_value_enter.displayText())
			# theta_value = float(self.theta_value_enter.displayText())
			energy_value = float(self.energy_value_enter.displayText())




			variableDict = {'Resolution':resolution_value, 
				   #'theta': theta_value, 
				   'Energy': energy_value, 'DetectorRadius': detectorradius_value}


			
			self.calculator.set_all_variables(variableDict)
			calculated_DetectorDistance = self.calculator.calcL()
			value_to_return = calculated_DetectorDistance
			self.detectordistance_value_enter.setText(str(calculated_DetectorDistance))
			self.calculator.set_variables('DetectorDistance', calculated_DetectorDistance)
			#setting checked key name so that it will change the bottom text
			checked_key = 'Detector distance (mm)'

		# elif checked_key == 'theta':

		# 	l_value = float(self.L_value_enter.displayText())
		# 	d_value = float(self.d_value_enter.displayText())
		# 	wave_value = float(self.wave_value_enter.displayText())


		# 	variableDict = {'DetectorDistance':l_value, 'Resolution': d_value, 'Energy': wave_value, 'DetectorRadius': r_value}

		# 	self.calculator.set_all_variables(variableDict)
		# 	# theta_value = self.calculator.calcTheta()
		# 	value_to_return = theta_value
		# 	# self.theta_value_enter.setText(str(theta_value))
		# 	# self.calculator.set_variables('theta', theta_value)
			


		elif checked_key == 'Energy':

			detectordistance_value = float(self.detectordistance_value_enter.displayText())
			# theta_value = float(self.theta_value_enter.displayText())
			resolution_value = float(self.resolution_value_enter.displayText())
			variableDict = {'DetectorDistance':detectordistance_value, 'Resolution': resolution_value, 
				   #'theta': theta_value, 
				   'DetectorRadius': detectorradius_value}


			
			self.calculator.set_all_variables(variableDict)
			energy_value = self.calculator.calcenergy()
			self.calculator.set_variables('Energy', energy_value)
			value_to_return = energy_value
			self.energy_value_enter.setText(str(energy_value))
			checked_key = 'Energy'
		

		

			



		self.bottom_text.setText("- Done Calculating - \n {} value = {}".format(checked_key, value_to_return))
		return value_to_return

		
def convertDetectorRadius(inputText):

	number = inputText[:inputText.find('mm')]

	return float(number)






if __name__ == '__main__':
	app = QApplication(sys.argv)
	window = CalculatorWindow()
	window.show()

	app.exec()