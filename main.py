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
    """Main window class of program for spectral plotting.
     Attributes:
         attr1 (list): sys.argv information.
    """
    def fits_plot(self):
        """
        Method for plotting spectrum from 1D FITS file.
        If plotting completed successfully, method will change text color in main window,
        else fits_plot will call fits_error_event for displaying IOError. 
        """
        try:
            fits_file = unicode(QFileDialog.getOpenFileName(self, 'Open FITS file'))
            if fits_file != '':
                header = fits.getheader(fits_file)
                dispersion_start = header['CRVAL1'] - (header['CRPIX1'] - 1) * header['CDELT1']
                linear_wcs = specwcs.Spectrum1DPolynomialWCS(degree=1, c0=dispersion_start, c1=header['CDELT1'],
                                                             unit='Angstrom')
                flux = fits.getdata(fits_file)
                spectrum = Spectrum1D(flux=flux, wcs=linear_wcs)
                wave = np.array(spectrum.wavelength)
                flux = np.array(spectrum.flux)
                self.pw.plot(wave, flux, pen=pg.mkColor(self.i))
                self.i += 2
        except IOError as exception:
            self.fits_error_event(exception.message)

    def fits_error_event(self, message):
        """
        Method creates window with error message, 
        when fits_plot raise IOError.
        :param message: The error message.
        """
        QMessageBox.critical(self, "IOError", "Can't read FITS file\n" + message)

    def closeEvent(self, event):
        """
        Method asking user about exit from application
        :param event: Accept close event
        """
        reply = QtGui.QMessageBox.question(self, 'Message',
                                           "Are you sure to quit?", QtGui.QMessageBox.Yes |
                                           QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def load_lines(self):
        """
        Method for plot spectrum lines with labels.
        Problems with flux < 10**-16
        """
        lines_data_file = unicode(QFileDialog.getOpenFileName(self, 'Open file'))

        if lines_data_file != '':
            lines_data = np.genfromtxt(lines_data_file, dtype=str)

            for i in range(len(lines_data[:, 0])):
                if i % 3 == 0:
                    line_label_position = 0.75
                elif i % 3 == 1:
                    line_label_position = 0.85
                else:
                    line_label_position = 0.90
                line = pg.InfiniteLine(pos=float(lines_data[i, 0]), label=str(lines_data[i, 1] + lines_data[i, 0]),
                                       labelOpts={'position': line_label_position, 'color': pg.mkColor("w")})
                line.setPen(style=QtCore.Qt.DotLine)
                self.pw.addItem(line)

    def table_plot(self):
        """
        Plot data from simple table.
        If plotting completed successfully, method will change text color in main window,
        else table_plot will call table_error_event for displaying IOError. 
        """
        try:
            file_name = unicode(QFileDialog.getOpenFileName(self, 'Open file'))
            if file_name != '':
                data = np.loadtxt(file_name)
                filtered_data = np.array([x for x in data if 2200 < x[0] < 8000])
                self.pw.plot(filtered_data[:, 0], filtered_data[:, 1], pen=pg.mkColor(self.i))
                self.i += 2
        except IOError as exception:
            self.table_error_event(exception.message)

    def table_error_event(self, message):
        """
        Method creates window with error message, 
        when table_plot raise IOError.
        :param message: The error message.
        """
        QMessageBox.critical(self, "IOError", "Can't read table file\n" + message)

    def clear_plot(self):
        """
        Remove all plots from widget and reset color
        """
        self.i = 0
        self.pw.clear()

    def cmfgen_plot(self):
        """
        Method for plotting spectrum from CMFGEN model.
        If plotting completed successfully, method will change text color in main window,
        else cmfgen_plot will call cmfgen_error_event for displaying IOError. 
        """
        try:
            cmfgen_filename = unicode(QFileDialog.getOpenFileName(self, 'Open file'))

            if cmfgen_filename != '':
                cmfgen_modeldata = cmfgenplot.spectr_input(cmfgen_filename)
                cmfgen_filename = cmfgen_filename[0:-3] + 'cont'
                cont = cmfgenplot.spectr_input(cmfgen_filename)
                f = interp1d(cont[:, 0], cont[:, 1])
                interpolated_data = f(cmfgen_modeldata[200:-200, 0])
                self.pw.plot(cmfgen_modeldata[ 200:-200, 0 ],
                               (cmfgen_modeldata[ 200:-200, 1 ] / interpolated_data), pen=pg.mkColor(self.i))
                self.i += 2
        except IOError as exception:
            self.cmfgen_error_event(exception.message)

    def cmfgen_error_event(self, message):
        """
        Method creates window with error message, 
        when cmfgen_plot raise IOError.
        :param message: The error message.
        """
        QMessageBox.critical(self, "IOError", "Can't read CMFGEN model file\n" + message)

    def __init__(self):
        """
        Инициализируем окно. Добавляем иконку.
        Создаем виджет для графики. Добавляем туда PlotWidget.
        TODO: Создаем графическое окно из которого можно удалять и добавлять графики.
        c1 = self.pw.plot(np.random.normal(size=100), pen=(255, 0, 0), name="Red curve")
        self.pw.removeItem(c1)
        """
        QtGui.QMainWindow.__init__(self)
        self.setWindowIcon(QIcon("web.png"))
        self.setWindowTitle('Plot Spectra')

        self.cw = QtGui.QWidget()
        self.setCentralWidget(self.cw)
        self.l = QtGui.QVBoxLayout()
        self.cw.setLayout(self.l)

        self.win = pg.GraphicsWindow()
        self.pw = self.win.addPlot()
        self.pw.showGrid(x=True, y=True)
        self.l.addWidget(self.win)
        self.i = 0


        openFile=QAction('Open from Table',self)
        openFile.setStatusTip('Open new File')
        openFile.triggered.connect(self.table_plot)

        loadLines=QAction('Load Lines',self)
        loadLines.setStatusTip('Load some Line')
        loadLines.triggered.connect(self.load_lines)

        clearPlot=QAction('Clear',self)
        clearPlot.setStatusTip('Clear plot')
        clearPlot.triggered.connect(self.clear_plot)

        cmfPlot=QAction('Open from CMFGEN',self)
        cmfPlot.setStatusTip('CMFGEN plot')
        cmfPlot.triggered.connect(self.cmfgen_plot)

        fitsPlot=QAction('Open from FITS',self)
        fitsPlot.setStatusTip('CMFGEN plot')
        fitsPlot.triggered.connect(self.fits_plot)

        menubar = self.menuBar()
        menubar.addAction(fitsPlot)
        menubar.addAction(openFile)
        menubar.addAction(cmfPlot)
        menubar.addAction(loadLines)
        menubar.addAction(clearPlot)


app = QtGui.QApplication(sys.argv)
main = MainWindow()
main.show()
sys.exit(app.exec_())
