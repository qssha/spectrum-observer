#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import matplotlib.pyplot as plt
from PyQt4.QtGui import QAction
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QMessageBox

from astropy.io import fits
from specutils.wcs import specwcs
from specutils import Spectrum1D
from scipy.interpolate import interp1d

import cmfgenplot  # Скрипт для парсера CMFGEN



class MainWindow(QtGui.QMainWindow):
    '''
    Импорт FITS одномерных спектров
    '''


    def v532Plot(self):

        specfilev532 = unicode(QFileDialog.getOpenFileName(self, 'Open v532 file'))



        if specfilev532 != '':

            contfilev532 = specfilev532[:-4] + "cont"

            #print(specfilev532, contfilev532)
            contfilev532 = np.loadtxt(contfilev532)
            specfilev532 = np.loadtxt(specfilev532)

            f = interp1d(contfilev532[:, 0], contfilev532[:, 1])
            newdata = f(specfilev532[:, 0])

            self.pw.plot(specfilev532[:, 0], ( newdata / specfilev532[:, 1]), pen=(1, self.i))

            self.i += 1
            '''
            header = fits.getheader(fitsfile)
            dispersion_start = header['CRVAL1'] - (header['CRPIX1'] - 1) * header['CDELT1']

            linear_wcs = specwcs.Spectrum1DPolynomialWCS(degree=1, c0=dispersion_start, c1=header['CDELT1'],
                                                         unit='Angstrom')

            flux = fits.getdata(fitsfile)

            myspec = Spectrum1D(flux=flux, wcs=linear_wcs)



            wave = np.array(myspec.wavelength)

            flux = np.array(myspec.flux)

            np.savetxt("some.data", zip(flux[0],flux[1]))


            self.pw.plot(flux[0], flux[1], pen=(1, self.i))

            self.i += 1
            '''


    def fitsPlot(self):

        fitsfile = unicode(QFileDialog.getOpenFileName(self, 'Open FITS file'))

        if fitsfile != '':

            header = fits.getheader(fitsfile)
            dispersion_start = header['CRVAL1'] - (header['CRPIX1'] - 1) * header['CDELT1']

            linear_wcs = specwcs.Spectrum1DPolynomialWCS(degree=1, c0=dispersion_start, c1=header['CDELT1'],
                                                         unit='Angstrom')

            flux = fits.getdata(fitsfile)

            myspec = Spectrum1D(flux=flux, wcs=linear_wcs)



            wave = np.array(myspec.wavelength)

            flux = np.array(myspec.flux)

            if np.mean(flux) < 10 ** -14: flux *= 10 ** 14

            self.pw.plot(wave, flux, pen=(1, self.i))
            self.i += 1

    '''
    Окно подтверждения при закрытии.
    '''

    def closeEvent(self, event):

        reply = QtGui.QMessageBox.question(self, 'Message',
                                           "Are you sure to quit?", QtGui.QMessageBox.Yes |
                                           QtGui.QMessageBox.No, QtGui.QMessageBox.No)

        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    '''
    Импорт данных из CMFGEN.
    '''

    def cmfgenplot(self):
        cmffile = QFileDialog.getOpenFileName(self, 'Open file')

        if cmffile != '':
            cmfdata = cmfgenplot.spectrinput(cmffile)

            #Временно названия только из гена
            '''
            ТЕСТИРОВАНИЕ
            '''

            cmffile = cmffile[0:-3] + 'cont'
            cont = cmfgenplot.spectrinput(cmffile)

            print(cmfdata[0,0])
            print(cont[0,0])

            f = interp1d(cont[:, 0], cont[:, 1])
            newdata = f(cmfdata[200:-200, 0])


            self.pw.plot(cmfdata[200:-200, 0], (cmfdata[200:-200, 1]/newdata), pen=(1, self.i))

            self.i += 1

            del (cmfdata, cmffile)

    '''
    Загрузить линии элементов из таблицы.
    '''

    def loadLines(self):
        linesfile = unicode(QFileDialog.getOpenFileName(self, 'Open file'))

        if linesfile != '':
            linedata = np.genfromtxt(linesfile, dtype=str)

            for i in range(len(linedata[:, 0])):
                if i % 3 == 0:
                    mypos = 0.75
                elif i % 3 == 1:
                    mypos = 0.85
                else:
                    mypos = 0.90
                line = pg.InfiniteLine(pos=float(linedata[i, 0]), label=str(linedata[i, 1] + linedata[i, 0]),
                                       labelOpts={'position': mypos, 'color': (200, 200, 255)})
                line.setPen(color=(200, 200, 255), style=QtCore.Qt.DotLine)
                self.pw.addItem(line)

                del (line)

            del (linesfile, linedata)

    '''
    Окно для загрузки графика в виде таблицы.
    '''

    def showDialog(self):
        fname = unicode(QFileDialog.getOpenFileName(self, 'Open file'))

        if fname != '':
            data = np.loadtxt(fname)
            filteredData = np.array([x for x in data if 3800 < x[0] < 7000])
            if np.mean(filteredData[:, 1]) < 10 ** -14:
                filteredData[:, 1] = filteredData[:, 1] * 10 ** 14
            p1 = self.pw.plot(filteredData[:, 0], filteredData[:, 1], pen=(1, self.i))

            self.i += 1
            del (fname, data, filteredData)

    '''
    Очистить графическое окно от всех элементов. Цвет = 1
    '''

    def clearPlot(self):
        self.i = 1
        self.pw.clear()

    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        '''
        Инициализируем окно. Добавляем иконку.
        '''

        self.setWindowIcon(QIcon("web.png"))

        self.setWindowTitle('Plot Spectra')

        '''
        Создаем виджет для графики. Добавляем туда PlotWidget.
        '''

        self.cw = QtGui.QWidget()
        self.setCentralWidget(self.cw)
        self.l = QtGui.QVBoxLayout()
        self.cw.setLayout(self.l)

        # self.pw = pg.PlotWidget(name='Plot')
        # self.pw.showGrid(x=True, y=True)

        # self.l.addWidget(self.pw)

        '''
        Создаем графическое окно из которого можно удалять и добавлять графики.
        c1 = self.pw.plot(np.random.normal(size=100), pen=(255, 0, 0), name="Red curve")
        self.pw.removeItem(c1)
        '''

        self.win = pg.GraphicsWindow()

        self.pw = self.win.addPlot()
        self.pw.showGrid(x=True, y=True)


        '''
        

        Для списка графиков надо создать словарь и хранить там имена!

        a = {}

        '''

        



        self.l.addWidget(self.win)

        '''
        Для разных цветов на графиках.
        '''

        self.i = 1

        '''
        Кнопки + бар. Сигналы и слоты.
        '''

        openFile = QAction('Open from Table', self)
        openFile.setStatusTip('Open new File')
        openFile.triggered.connect(self.showDialog)

        loadLines = QAction('Load Lines', self)
        loadLines.setStatusTip('Load some Line')
        loadLines.triggered.connect(self.loadLines)

        clearPlot = QAction('Clear', self)
        clearPlot.setStatusTip('Clear plot')
        clearPlot.triggered.connect(self.clearPlot)

        cmfPlot = QAction('Open from CMFGEN', self)
        cmfPlot.setStatusTip('CMFGEN plot')
        cmfPlot.triggered.connect(self.cmfgenplot)

        fitsPlot = QAction('Open from FITS', self)
        fitsPlot.setStatusTip('CMFGEN plot')
        fitsPlot.triggered.connect(self.fitsPlot)


        v532Plot = QAction('Open v532', self)
        v532Plot.setStatusTip('v532 plot')
        v532Plot.triggered.connect(self.v532Plot)

        menubar = self.menuBar()
        menubar.addAction(fitsPlot)
        menubar.addAction(openFile)
        menubar.addAction(cmfPlot)
        menubar.addAction(loadLines)
        menubar.addAction(clearPlot)
        menubar.addAction(v532Plot)


app = QtGui.QApplication(sys.argv)

main = MainWindow()
main.showMaximized()
sys.exit(app.exec_())
