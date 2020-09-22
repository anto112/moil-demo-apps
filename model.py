import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from Ui import *
import cv2
import numpy as np
from Moildev import Moildev
from ConfigData import Config
from image_resize import image_resize
import datetime


class model(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.videoStreamURL = 'http://192.168.100.204:8000/stream.mjpg'
        self.filename = "./parameter/picamera.json"
        self.config = Config(self.filename)
        self.image = None
        self.mode = None
        self.image_result = None
        self.height = 700
        self.angle = 0
        self.zoom = 4
        self.beta = 0
        self.alpha = 0
        self.max = 110
        self.min = 0
        self.cap = None
        self.anypoint = False
        self.pano = False
        self.normal = False
        self.panoX = False
        self.anypointState = 1
        self.connect_event()
        self.ui.any_mode_1.setChecked(True)
        self.initMoildev()
        self.disableRadio_any()
        self.ui.groupBox_4.hide()

    def connect_event(self):
        self.ui.actionExit.triggered.connect(self.onclick_exit)
        self.ui.actionAbout_Us.triggered.connect(self.onclick_aboutUs)
        self.ui.open_image.clicked.connect(self.open_image)
        self.ui.normal_view.clicked.connect(self.normal_view)
        self.ui.rotate_left.clicked.connect(self.rotate_left)
        self.ui.rotate_right.clicked.connect(self.rotate_right)
        self.ui.anypoint_view.clicked.connect(self.anypoint_view)
        self.ui.panorama_view.clicked.connect(self.onclick_panorama_view)
        self.ui.set_anypoint.clicked.connect(self.set_anyPoint)
        self.ui.any_mode_1.clicked.connect(self.onclick_radio_mode1)
        self.ui.any_mode_2.clicked.connect(self.onclick_radio_mode2)
        self.ui.set_panorama.clicked.connect(self.set_pano)
        self.ui.actionLoad_Parameter.triggered.connect(self.load_param)
        self.ui.actionOpen_Image.triggered.connect(self.open_image)
        self.ui.panoX_view.clicked.connect(self.onclickPanoramaX)

    def initMoildev(self):
        self.camera = self.config.get_cameraName()
        self.sensor_width = self.config.get_sensorWidth()
        self.sensor_height = self.config.get_sensor_height()
        self.Icx = self.config.get_Icx()
        self.Icy = self.config.get_Icy()
        self.ratio = self.config.get_ratio()
        self.imageWidth = self.config.get_imageWidth()
        self.imageHeight = self.config.get_imageHeight()
        self.calibrationRatio = self.config.get_calibrationRatio()
        self.parameter0 = self.config.get_parameter0()
        self.parameter1 = self.config.get_parameter1()
        self.parameter2 = self.config.get_parameter2()
        self.parameter3 = self.config.get_parameter3()
        self.parameter4 = self.config.get_parameter4()
        self.parameter5 = self.config.get_parameter5()
        self.moildev = Moildev(self.camera, self.sensor_width, self.sensor_height, self.Icx, self.Icy, self.ratio,
                               self.imageWidth, self.imageHeight, self.parameter0, self.parameter1, self.parameter2,
                               self.parameter3, self.parameter4, self.parameter5, self.calibrationRatio)
        self.ui.lineEdit.setText(str(self.camera))

    def init_Map(self):
        self.h, self.w = self.image_ori.shape[:2]
        self.ratio_x = self.w / 400
        self.ratio_y = self.h / 300
        self.center = (round(200 * self.ratio_x), round(150 * self.ratio_y))
        self.size = self.h, self.w, 3
        self.cx = round(self.w / 2)
        self.cy = round(self.h / 2)
        self.res = np.zeros(self.size, dtype=np.uint8)
        calibrationWidth = self.imageWidth
        self.m_ratio = self.w / calibrationWidth
        self.mapX = np.zeros((self.h, self.w), dtype=np.float32)
        self.mapY = np.zeros((self.h, self.w), dtype=np.float32)

    def disableRadio_any(self):
        self.ui.groupBox.hide()
        self.ui.groupBox_3.hide()

    def enableRadio_any(self):
        self.ui.groupBox.show()
        self.ui.groupBox_3.show()

    def view_original(self):
        if self.anypoint:
            self.img = cv2.resize(self.img_any, (400, 300), interpolation=cv2.INTER_AREA)
        else:
            self.img = cv2.resize(self.image_ori, (400, 300), interpolation=cv2.INTER_AREA)
        my_label = self.ui.original_source
        image = QtGui.QImage(self.img.data, self.img.shape[1], self.img.shape[0],
                             QtGui.QImage.Format_RGB888).rgbSwapped()
        my_label.setPixmap(QtGui.QPixmap.fromImage(image))

    def view_result(self):
        main_w = self.ui.Main_window
        normal_image = QtGui.QImage(self.image_result.data, self.image_result.shape[1],
                                    self.image_result.shape[0],
                                    QtGui.QImage.Format_RGB888).rgbSwapped()
        main_w.setPixmap(QtGui.QPixmap.fromImage(normal_image))

    def load_param(self):
        """get parameter"""
        dialog = QtWidgets.QFileDialog()
        options = dialog.DontResolveSymlinks | dialog.ShowDirsOnly
        self.filename, _filter = dialog.getOpenFileName(dialog, 'Select Parameter',
                                                        filter="Image files (*.json *.txt)",
                                                        options=options)
        if len(self.filename) == 0:
            pass
        else:
            self.config = Config(self.filename)
        self.initMoildev()

    def open_image(self):
        dialog = QtWidgets.QFileDialog()
        options = dialog.DontResolveSymlinks | dialog.ShowDirsOnly
        self.filename, _filter = dialog.getOpenFileName(dialog, 'Select image',
                                                        filter="Image files (*.jpg *.png)",
                                                        options=options)
        if len(self.filename) == 0:
            pass
        else:
                self.image = cv2.imread(self.filename)
                self.image_ori = self.image.copy()
                self.view_original()
                self.normal_view()
                self.ui.normal_view.setChecked(True)
                self.init_Map()
                self.ui.original_source.mouseReleaseEvent = self.mouseRelease
                self.ui.original_source.mouseDoubleClickEvent = self.mouseDoubleClick
                self.ui.plus_icon.mouseDoubleClickEvent = self.mouseDoubleClick

    def normal_view(self):
        self.anypoint = False
        self.pano = False
        self.normal = True
        self.panoX = False
        self.ui.panoX_view.setChecked(False)
        if self.image is None:
            pass
        else:
            self.view_original()
            self.disableRadio_any()
            self.ui.groupBox_4.hide()
            self.result = self.image.copy()  # image after reconstruction center
            self.image_result = image_resize(self.result, self.height)
            self.view_result()

    def anypoint_view(self):
        self.anypoint = True
        self.pano = False
        self.normal = False
        self.panoX = False
        self.ui.panoX_view.setChecked(False)
        if self.image is None:
            pass
        else:
            self.enableRadio_any()
            self.ui.groupBox_4.hide()
            if self.ui.any_mode_1.isChecked():
                self.show_anypoint_mode_1()
            elif self.ui.any_mode_2.isChecked():
                self.show_anypoint_mode_2()
            self.ui.edit_alpha.setText("%0.2f" % self.alpha)
            self.ui.edit_beta.setText("%0.2f" % self.beta)
            self.ui.edit_zoom.setText(str(self.zoom))
            self.polygon_anypoint()
            self.display_ori()

    def show_anypoint_mode_1(self):
        self.anypointState = 0
        if self.beta < 0:
            self.beta = self.beta + 360
        if self.alpha < -90 or self.alpha > 90 or self.beta < 0 or self.beta > 360:
            self.alpha = 0
            self.beta = 0
        else:
            self.alpha = -90 if self.alpha < -90 else self.alpha
            self.alpha = 90 if self.alpha > 90 else self.alpha
            self.beta = 0 if self.beta < 0 else self.beta
            self.beta = 360 if self.beta > 360 else self.beta

        self.moildev.AnyPointM(self.mapX, self.mapY, self.w, self.h, self.alpha, self.beta, self.zoom, self.m_ratio)
        self.result = cv2.remap(self.image_ori, self.mapX, self.mapY, cv2.INTER_CUBIC)
        self.image_result = image_resize(self.result, self.height)
        self.view_result()

    def show_anypoint_mode_2(self):
        self.anypointState = 1
        if self.alpha < - 90 or self.alpha > 90 or self.beta < -90 or self.beta > 90:
            self.alpha = 0
            self.beta = 0
        else:
            self.alpha = -90 if self.alpha < -90 else self.alpha
            self.alpha = 90 if self.alpha > 90 else self.alpha
            self.beta = -90 if self.beta < -90 else self.beta
            self.beta = 90 if self.beta > 90 else self.beta
        self.moildev.AnyPointM2(self.mapX, self.mapY, self.w, self.h, self.alpha, self.beta, self.zoom, self.m_ratio)
        self.result = cv2.remap(self.image_ori, self.mapX, self.mapY, cv2.INTER_CUBIC)
        self.image_result = image_resize(self.result, self.height)
        self.view_result()

    def onclick_radio_mode1(self):
        if self.ui.any_mode_1.isChecked():
            self.alpha = 0
            self.beta = 0
            self.anypoint_view()
        else:
            pass

    def onclick_radio_mode2(self):
        if self.ui.any_mode_2.isChecked():
            self.alpha = 0
            self.beta = 0
            self.anypoint_view()
        else:
            pass

    def set_anyPoint(self):
        self.alpha = float(self.ui.edit_alpha.text())
        self.beta = float(self.ui.edit_beta.text())
        self.zoom = float(self.ui.edit_zoom.text())
        self.anypoint_view()

    def onclick_panorama_view(self):
        self.anypoint = False
        self.pano = True
        self.normal = False
        self.panoX = False
        self.ui.panoX_view.setChecked(False)
        if self.image is None:
            pass
        else:
            self.alpha = 0
            self.beta = 0
            self.min = 0
            self.view_original()
            self.disableRadio_any()
            self.ui.groupBox_4.show()
            self.panorama()

    def panorama(self):
        self.moildev.PanoramaM_Rt(self.mapX, self.mapY, self.w, self.h, self.m_ratio, self.max, self.alpha, self.beta)
        self.result = cv2.remap(self.image_ori, self.mapX, self.mapY, cv2.INTER_CUBIC)
        self.image_result = image_resize(self.result, self.height)
        self.view_result()
        self.ui.edit_max.setText(str(self.max))
        self.ui.edit_min.setText(str(self.min))

    def onclickPanoramaX(self):
        self.anypoint = False
        self.pano = False
        self.normal = False
        self.panoX = True
        if self.image is None:
            pass
        else:
            self.alpha = 0
            self.beta = 0
            self.min = 10
            self.view_original()
            self.disableRadio_any()
            self.ui.groupBox_4.show()
            self.panoramaX()

    def panoramaX(self):
        self.moildev.PanoramaX(self.mapX, self.mapY, self.w, self.h, self.m_ratio, self.max, self.min)
        self.result = cv2.remap(self.image_ori, self.mapX, self.mapY, cv2.INTER_CUBIC)
        self.image_result = image_resize(self.result, self.height)
        self.view_result()
        self.ui.edit_max.setText(str(self.max))
        self.ui.edit_min.setText(str(self.min))

    def set_pano(self):
        self.max = int(self.ui.edit_max.text())
        self.min = int(self.ui.edit_min.text())
        if self.pano:
            self.panorama()
        elif self.panoX:
            self.panoramaX()
        else:
            pass

    def display_ori(self):
        self.img_any = self.image.copy()
        if self.alpha == 0:
            cv2.circle(self.img_any, self.center, 25, (0, 255, 0), 6, -1)
        else:
            cv2.circle(self.img_any, (self.pos_x, self.pos_y), 25, (0, 255, 0), 6, -1)
        cv2.polylines(self.img_any, np.int32([self.points]), False, (0, 125, 255), 10)
        cv2.polylines(self.img_any, np.int32([self.points2]), False, (0, 125, 255), 10)
        cv2.polylines(self.img_any, np.int32([self.points3]), False, (0, 125, 255), 10)
        cv2.polylines(self.img_any, np.int32([self.points4]), False, (0, 125, 255), 10)
        self.img_any = cv2.resize(self.img_any, (400, 300), interpolation=cv2.INTER_AREA)
        self.view_original()

    def polygon_anypoint(self):
        X1 = [];  Y1 = []
        X2 = [];  Y2 = []
        X3 = [];  Y3 = []
        X4 = [];  Y4 = []

        x = 0
        while x < self.w:
            a = self.mapX[0,]
            b = self.mapY[0,]
            e = self.mapX[-1,]
            f = self.mapY[-1,]

            if a[x] == 0. or b[x] == 0.:
                pass
            else:
                X1.append(a[x])
                Y1.append(b[x])

            if f[x] == 0. or e[x] == 0.:
                pass
            else:
                Y3.append(f[x])
                X3.append(e[x])
            x += 10

        y = 0
        while y < self.h:
            c = self.mapX[:, 0]
            d = self.mapY[:, 0]
            g = self.mapX[:, -1]
            h = self.mapY[:, -1]
            if d[y] == 0. or c[y] == 0.:  # or d[y] and c[y] == 0.0:
                pass

            else:
                Y2.append(d[y])
                X2.append(c[y])

            if h[y] == 0. or g[y] == 0.:
                pass
            else:
                Y4.append(h[y])
                X4.append(g[y])
            y += 10

        p = np.array([X1, Y1]);
        q = np.array([X2, Y2])
        r = np.array([X3, Y3]);
        s = np.array([X4, Y4])
        self.points = p.T.reshape((-1, 1, 2));
        self.points2 = q.T.reshape((-1, 1, 2))
        self.points3 = r.T.reshape((-1, 1, 2));
        self.points4 = s.T.reshape((-1, 1, 2))

    def mousePress(self, e):
        """ Get the position coordinate from mouse event"""
        if e.button() == QtCore.Qt.LeftButton:
            pass

    def wheelEvent(self, e):
        wheelcounter = e.angleDelta()
        if wheelcounter.y() / 120 == 1:
            self.zoom_in()
        if wheelcounter.y() / 120 == -1:
            self.zoom_out()

    def mouseRelease(self, e):
        # self.ui.original_source.mouseReleaseEvent(self, e)
        if e.button() == QtCore.Qt.LeftButton:
            self.currPos = e.pos()
            self.pos_x = round(e.x() * self.ratio_x)
            self.pos_y = round(e.y() * self.ratio_y)
            delta_x = round(self.pos_x - self.w * 0.5)
            delta_y = round(- (self.pos_y - self.h * 0.5))
            self.alpha, self.beta = self.config.get_alpha_beta(self.anypointState, delta_x, delta_y)
            if self.anypoint:
                self.anypoint_view()
            elif self.pano:
                self.panorama()
            elif self.normal:
                self.alpha = 0
                self.beta = 0
            else:
                pass

    def saveImage(self):
        ss = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
        filename = "result/ss_" + str(ss) + ".png"
        if self.image is None:
            pass

        else:
            cv2.imwrite(filename, self.result)
            msgbox = QtWidgets.QMessageBox()
            msgbox.setWindowTitle("Save File")
            msgbox.setText("\nImage saved succeed !!")
            msgbox.setIconPixmap(QtGui.QPixmap('assets/check.png'))
            msgbox.exec()

    def mouseDoubleClick(self, e):
        if self.anypoint:
            self.alpha = 0
            self.beta = 0
            self.zoom = 4
            self.anypoint_view()
        elif self.pano:
            self.alpha = 0
            self.beta = 0
            self.onclick_panorama_view()
        elif self.normal:
            self.alpha = 0
            self.beta = 0
            self.height = 700
            self.normal_view()
        else:
            pass

    def zoom_in(self):
        if self.image is None:
            pass
        else:
            if self.anypoint:
                if self.zoom == 14:
                    pass
                else:
                    self.zoom += 1
                    self.anypoint_view()

            elif self.pano:
                pass

            elif self.normal:
                if self.height == 2000:
                    pass
                else:
                    self.height += 100
                    self.normal_view()

    def zoom_out(self):
        if self.image is None:
            pass
        else:
            if self.anypoint:
                if self.zoom == 1:
                    pass
                else:
                    self.zoom -= 1
                    self.anypoint_view()
            elif self.pano:
                pass

            elif self.normal:
                if self.height == 700:
                    pass
                else:
                    self.height -= 100
                    self.normal_view()

    def rotate_left(self):
        if self.image is None:
            pass
        else:
            if self.angle == 180:
                pass
            else:
                self.angle += 10
                self.rotate_image()

    def rotate_right(self):
        if self.image is None:
            pass
        else:
            if self.angle == -180:
                pass
            else:
                self.angle += -10
                self.rotate_image()

    def rotate_image(self):
        self.res = self.moildev.Rotate(self.w, self.h, self.result, self.angle)
        self.image_result = image_resize(self.res, self.height)
        self.view_result()

    def onclick_aboutUs(self):
        msgbox = QtWidgets.QMessageBox()
        msgbox.setWindowTitle("About Us")
        msgbox.setText(
            "MOIL \n\nOmnidirectional Imaging & Surveillance Lab\nMing Chi University of Technology\n\nContact: M07158031@0365.mcut.edu.tw")
        msgbox.setIconPixmap(QtGui.QPixmap('./assets/chess.jpg'))
        msgbox.exec()

    def onclick_exit(self):
        self.close()
