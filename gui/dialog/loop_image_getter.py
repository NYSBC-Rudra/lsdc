import logging
import typing
from PIL import Image
from io import BytesIO
import urllib

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
        self.setFixedSize(200, 300)

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
        setcheck= False
        while setcheck != True:
            #add md2 through control_main
            state = self.md2.exporter.read('OmegaState')
            if state == 'Ready':
                setcheck  = True

        self.current_omega = self.md2.omega.get()[0]
        return

    def setOmega(self, omega):
        self.md2.omega.set(omega)
        self.getOmega()
        return
    
    def saveImage(self, name):
        file = BytesIO(urllib.request.urlopen('http://10.67.147.26:3908/video_feed2', timeout=1000/1000).read())
        image = Image.open(file)
        image_bytes = BytesIO()
        image.save(image_bytes, format='JPEG')
        image_bytes = image_bytes.getvalue()
        image_bytes.save('{}.jpg'.format(name))
        return
    
    def runLoop(self):
        try:
            total_rotation = float(self.total_rotation.text())
            interval = float(self.interval.text())
        except:
            logger.info('Not a valid float for either rotation or interval')
            return

        for i in range(self.current_omega, self.current_omega + total_rotation+1, interval):
            name = '{}_{}-{}'.format(str(self.current_omega), str(i), str(total_rotation) )
            self.saveImage(name)
            self.setOmega(i)

        return
