import numpy as np
import math
import json
import csv


class Config:
    def __init__(self, filename):
        super(Config, self).__init__()
        self.PI = 3.1415926
        self.alphaToRho_Table = []
        self.rhoToAlpha_Table = []

        """setting default parameter"""
        if filename is None:
            pass
        else:
            with open(filename) as f:
                data = json.load(f)
            self.camera = data["cameraName"]
            self.sensor_width = data['cameraSensorWidth']
            self.sensor_height = data['cameraSensorHeight']
            self.Icx = data['iCx']
            self.Icy = data['iCy']
            self.ratio = data['ratio']
            self.imageWidth = data['imageWidth']
            self.imageHeight = data['imageHeight']
            self.calibrationRatio = data['calibrationRatio']
            self.parameter0 = data['parameter0']
            self.parameter1 = data['parameter1']
            self.parameter2 = data['parameter2']
            self.parameter3 = data['parameter3']
            self.parameter4 = data['parameter4']
            self.parameter5 = data['parameter5']

        self.initAlphaRho_Table()

    def get_cameraName(self):
        return self.camera

    def get_sensorWidth(self):
        return self.sensor_width

    def get_sensor_height(self):
        return self.sensor_height

    def get_Icx(self):
        return self.Icx

    def get_Icy(self):
        return self.Icy

    def get_ratio(self):
        return self.ratio

    def get_imageWidth(self):
        return self.imageWidth

    def get_imageHeight(self):
        return self.imageHeight

    def get_calibrationRatio(self):
        return self.calibrationRatio

    def get_parameter0(self):
        return self.parameter0

    def get_parameter1(self):
        return self.parameter1

    def get_parameter2(self):
        return self.parameter2

    def get_parameter3(self):
        return self.parameter3

    def get_parameter4(self):
        return self.parameter4

    def get_parameter5(self):
        return self.parameter5

    def initAlphaRho_Table(self):
        for i in range(1800):
            alpha = i / 10 * 3.1415926 / 180
            self.alphaToRho_Table.append((self.parameter0 * alpha * alpha * alpha * alpha * alpha * alpha
                                          + self.parameter1 * alpha * alpha * alpha * alpha * alpha
                                          + self.parameter2 * alpha * alpha * alpha * alpha
                                          + self.parameter3 * alpha * alpha * alpha
                                          + self.parameter4 * alpha * alpha
                                          + self.parameter5 * alpha) * self.calibrationRatio)
            i += 1

        i = 0
        index = 0
        while i < 1800:
            while index < self.alphaToRho_Table[i]:
                self.rhoToAlpha_Table.append(i)
                index += 1
            i += 1

        while index < 3600:
            self.rhoToAlpha_Table.append(i)
            index += 1

    def getAlphaFromRho(self, rho):
        if rho >= 0:
            return self.rhoToAlpha_Table[rho] / 10
        else:
            return -self.rhoToAlpha_Table[-rho] / 10

    def getRhoFromAlpha(self, alpha):
        return self.alphaToRho_Table[round(alpha * 10)]

    def get_alpha_beta(self, mode, delta_x, delta_y):
        if mode == 0:
            r = round(math.sqrt(math.pow(delta_x, 2) + math.pow(delta_y, 2)))
            alpha = self.getAlphaFromRho(r)

            if delta_x == 0:
                angle = 0
            else:
                angle = (math.atan2(delta_y, delta_x) * 180) / self.PI

            beta = 90 - angle

        else:
            alpha = self.getAlphaFromRho(delta_y)
            beta = self.getAlphaFromRho(delta_x)

        return alpha, beta

