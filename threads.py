from qtpy.QtCore import QThread, QTimer, QEventLoop, Signal, QPoint, Qt, QObject
from qtpy import QtGui
from PIL import Image, ImageQt
import cv2
import os
import sys
import urllib
from urllib.parse import urlparse
from io import BytesIO
import logging
from config_params import SERVER_CHECK_DELAY
import raddoseLib
import cv2
import time
import numpy as np
import requests
import redis
import re

logger = logging.getLogger()


class VideoThread(QThread):
    frame_ready = Signal(object)

    def __init__(self, *args, delay=1000, url='', camera_object=None, width=None, height=None,**kwargs):
        self.delay = delay
        self.width = width
        self.height = height
        self.url = url
        self.camera_object = CameraObject(camera_object, url) if camera_object or url else None
        self.showing_error = False
        self.is_running = True
        QThread.__init__(self, *args, **kwargs)

    def camera_refresh(self):
        pixmap_orig = QtGui.QPixmap(320, 180)
        if self.camera_object:
            try:
                qimage = self.camera_object.getfunction()
                pixmap_orig = QtGui.QPixmap.fromImage(qimage)
                self.showing_error = False
            except Exception as e:
                if not self.showing_error:
                    painter = QtGui.QPainter(pixmap_orig)
                    painter.setPen(QtGui.QPen(Qt.white))
                    painter.drawText( QPoint(10, 10), "No image obtained from: " )
                    painter.drawText( QPoint(10, 30), f"{self.url}")
                    painter.end()
                    self.frame_ready.emit(pixmap_orig)
                    self.showing_error = True

        if not self.showing_error:
            self.frame_ready.emit(pixmap_orig)

    def run(self):
        while self.is_running:
            self.camera_refresh()
            self.msleep(self.delay)

    def stop(self):
        self.is_running = False

    def updateCam(self, camera_object):
        self.camera_object = CameraObject(camera_object, self.url)


class RaddoseThread(QThread):
    lifetime = Signal(float)
    def __init__(self, *args, avg_dwd = 10, #Default of 10MGy 
                beamsizeV = 1.0, beamsizeH = 2.0,
                vectorL = 0.0,
                energy = 12.66,
                flux = -1.0,
                wedge = 180.0,
                verbose = False, **kwargs):
        self.avg_dwd = avg_dwd
        self.beamsizeV = beamsizeV
        self.beamsizeH = beamsizeH
        self.vectorL = vectorL
        self.energy = energy
        self.flux = flux
        self.wedge = wedge
        self.verbose = verbose
        QThread.__init__(self, *args, **kwargs)

    def run(self):
        lifetime_value = raddoseLib.fmx_expTime(self.avg_dwd, self.beamsizeV, self.beamsizeH, self.vectorL, self.energy, self.flux, self.wedge, self.verbose)
        self.lifetime.emit(lifetime_value)


class ServerCheckThread(QThread):
    visit_dir_changed = Signal()
    def __init__(self, *args, delay=SERVER_CHECK_DELAY, **kwargs):
        self.delay = delay
        QThread.__init__(self, *args, **kwargs)

    def run(self):
        import db_lib
        beamline = os.environ["BEAMLINE_ID"]
        while True:
            if db_lib.getBeamlineConfigParam(beamline, "visitDirectory") != os.getcwd():
                message = "The server visit directory has changed, stopping!"
                logger.error(message)
                print(message)
                self.visit_dir_changed.emit()
                break
            self.msleep(self.delay)




#Making camera object class for future use, incase any new forms of videos are outputted.
'''
@variables
    - camera
    the camera object (either a cv2.videocapture object, a redis.connection, or a link)
    - type
    type of camera object (for now either "cv2", "redis", or "url")
    - getfunction
    the required function to get an image (should change in init)
    - key
    redis key incase of redis connection
@inputs
    - objecturl
    url of the stream for the camera object to connect to
    - url
    url of the stream if uses defined with url in videostreamer
@functions
    - setupUrlConnection
    makes camera object if the input is a URL
    - setupObjectConnection
    same but if camera_object is input not URL
    - xGet
    currently for redis, cv2, and a generic http jpeg image. will get the image and return a qimage object
'''

'''
all input links are in the form
function://ip:port/key
for example
redis://10.67.146.131:6379/bzoom:RAW

'''

class CameraObject():

    '''
    all xGet functions return a qimage object 
    
    
    '''
    def cv2Get(self):
        self.camera.set(cv2.CAP_PROP_POS_FRAMES, 0)
        most_recent_frame = None

        timeout = self.delay / 1000.0
        start_time = time.time()
        if self.camera.grab():
            retval, frame = self.camera.retrieve()
            if retval:
                most_recent_frame = frame
        self.currentFrame = most_recent_frame

        if self.currentFrame is None:
            #logger.debug('no frame read from stream URL - ensure the URL does not end with newline and that the filename is correct')
            return

        height,width=self.currentFrame.shape[:2]
        qimage= QtGui.QImage(self.currentFrame,width,height,3*width,QtGui.QImage.Format_RGB888)
        qimage = qimage.rgbSwapped()
        return qimage



    def redisGet(self):
        data = self.camera.get(self.key)
        image = Image.frombuffer("RGB", (640,512), data)
        qimage = ImageQt.ImageQt(image)
        return qimage

    def urlGet(self):
        file = BytesIO(urllib.request.urlopen(self.url, timeout=self.delay/1000).read())
        img = Image.open(file)
        qimage = ImageQt.ImageQt(img)
        return qimage

    '''
    returns the type of the link
    '''
    def setupObjectConnection(self, objecturl):
        cv2match = re.match(r'http://([\d\.]+):(\d+)/(.+)', objecturl)
        #Splits link into http:// ip : port / key
        self.camera = cv2.VideoCapture(cv2match.group(0))
        self.camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.type = "cv2"
        self.getfunction = self.cv2Get
        self.key = cv2match.group(3)
        self.url = cv2match.group(0)
        if self.camera.grab():
            retval, frame = self.camera.retrieve()
            if retval:
                most_recent_frame = frame
        self.currentFrame = most_recent_frame
        return self.type

    def setupUrlConnection(self, url):
        #parsing URL using urlparse
        split_url = urlparse(url)

        self.scheme = split_url.scheme
        self.host = split_url.hostname
        self.port = split_url.port
        #removing the / in the path
        self.key = split_url.path[1:]
        self.query = split_url.query

        #checking netloc to see if there is a formatting problem in the input string
        if self.scheme == 'redis' and split_url.netloc != '':
            #parse url
            #ip = redismatch.group(1)
            #port = redismatch.group(2)
            #self.key = redismatch.group(3)
            self.camera = redis.StrictRedis(host=self.host, port=self.port, db=0)
            self.type='redis'
            self.getfunction = self.redisGet
            self.url = split_url
            return self.type
        elif self.scheme == 'https' and split_url.netloc != '':
            self.key = url
            self.type = 'url'
            self.getfunction = self.urlGet
            self.url = url
            return self.type
        else:
            message = 'incorrect camera object function init. stopping!'
            logger.error(message)
            return


 #IF inputting with both and obejct url and url it will use the url input 
    def __init__(self, objecturl, url):
        self.getfunction = None
        self.camera = None
        self.key = None
        self.type = None
        self.url = None
        self.currentFrame = None
        if objecturl != None:
            self.setupObjectConnection(objecturl)

        elif url != '':
            self.setupUrlConnection(url)  

        else:
            message = "link for cameraobject does not start with http or redis, stopping!"
            logger.error(message)
            return


        if None in [self.getfunction, self.camera, self.key, self.type, self.url]:
            message = 'incorrect camera object function init. stopping!'

            logger.error(message)
            return