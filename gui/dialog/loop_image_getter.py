import logging
import typing
from PIL import Image
from io import BytesIO
import urllib.request

from qtpy import QtCore, QtGui, QtWidgets
from qtpy.QtCore import Qt
from qtpy import uic




if typing.TYPE_CHECKING:
    from lsdcGui import ControlMain

logger = logging.getLogger()

class OmegaRotatorDialog(QtWidgets.QDialog):
    def __init__(self,md2, parent: "ControlMain"):
        super(OmegaRotatorDialog, self).__init__(parent)
        self.md2 = md2
        self.current_omega = self.getOmega()
        self.initUI()

    def initUI(self):
        self.setFixedSize(300, 400)

        layout = QtWidgets.QVBoxLayout()

        total_rotation_label = QtWidgets.QLabel("Total Rotation (use negative to go the other way):")
        self.total_rotation = QtWidgets.QLineEdit()

        interval_label = QtWidgets.QLabel("Interval (make negative if total rotation is negative):")
        self.interval = QtWidgets.QLineEdit()

        button_label = QtWidgets.QLabel("Run loop:")
        self.button = QtWidgets.QPushButton("Submit")
        self.button.clicked.connect(self.runLoop)

        layout.addWidget(total_rotation_label)
        layout.addWidget(self.total_rotation)

        layout.addWidget(interval_label)
        layout.addWidget(self.interval)

        layout.addWidget(button_label)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def getOmega(self):
        self.current_omega = self.md2.omega.get()[0]
        #logger.info('{}: current omega from running getOmega'.format(str(self.current_omega)))
        return

    def setOmega(self, omega):
        self.md2.omega.set(omega)
        self.current_omega = omega
        return
    
    def saveImage(self, name):
        myfile = BytesIO(urllib.request.urlopen('http://10.67.147.26:3908/video_feed2', timeout=1000/1000).read())
        image = Image.open(myfile)
        image.save('{}.jpg'.format(name), format='JPEG')
        return
    
    def runLoop(self, do_not_spin=False):
        try:
            total_rotation = float(self.total_rotation.text())
            interval = float(self.interval.text())
            self.getOmega()
        except:
            logger.info('Not a valid float for either rotation or interval')
            return
        logger.info('Starting rotation from {}'.format(str(self.current_omega)))
        logger.info('Total rotation is {}'.format(str(total_rotation)))
        logger.info('interval is {}'.format(str(interval)))

        max_value = int(self.current_omega + total_rotation)
        if total_rotation < 0:
            max_value = max_value - 1
        else:
            max_value = max_value +1
        current_value = int(self.current_omega)


        while(abs(current_value - max_value) > abs(interval)):

            state = self.md2.exporter.read('OmegaState')
            if state == 'Ready':
                self.getOmega()

                next_value = self.current_omega + interval
                file_name = '{}_{}-{}'.format(str(int(self.current_omega)), str(int(next_value)), str(int(total_rotation)) )
                self.saveImage(file_name)


                logger.info('Setting omega to {}'.format(str(next_value)))

                current_value = next_value
                if do_not_spin==False:
                    self.setOmega(current_value)
        return





