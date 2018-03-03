#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtGui, QtCore
import pyqtgraph as pg
import numpy as np
import matplotlib.pyplot as plt
from PyQt4.QtGui import QAction, QPushButton, QListWidget, QListWidgetItem
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
        Call add_to_list_widget with plot item name.
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
                current_plot = self.pw.plot(wave, flux, pen=pg.mkColor(self.i))
                plot_name = fits_file.split("/")[-1]
                self.all_plot_items[plot_name] = current_plot
                self.add_to_list_widget(plot_name)
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
        Call add_to_list_widget with plot item name.
        """
        try:
            file_name = unicode(QFileDialog.getOpenFileName(self, 'Open two-column table data file'))
            if file_name != '':
                data = np.loadtxt(file_name)
                filtered_data = np.array([x for x in data if 2200 < x[0] < 8000])
                current_plot = self.pw.plot(filtered_data[:, 0], filtered_data[:, 1], pen=pg.mkColor(self.i))
                plot_name = file_name.split("/")[-1]
                self.all_plot_items[plot_name] = current_plot
                self.add_to_list_widget(plot_name)
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
        self.all_plot_items = {}
        self.listWidget.clear()

    def cmfgen_plot(self):
        """
        Method for plotting spectrum from CMFGEN model.
        If plotting completed successfully, method will change text color in main window,
        else cmfgen_plot will call cmfgen_error_event for displaying IOError.
        Call add_to_list_widget with plot item name.
        """
        try:
            cmfgen_filename = unicode(QFileDialog.getOpenFileName(self ,'Open CMFGEN model file'))

            if cmfgen_filename != '':
                reply = QMessageBox.question(self, 'Message', "Do you want to plot normilized spectrum from *cont file?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

                x_limit_left = 3800
                x_limit_right = 8000
                cmfgen_modeldata = cmfgenplot.spectr_input(cmfgen_filename)
                cmfgen_modeldata = cmfgen_modeldata[:np.where(cmfgen_modeldata[:, 0] < x_limit_right)[0][-1], :]
                cmfgen_modeldata = cmfgen_modeldata[np.where(cmfgen_modeldata[:, 0] > x_limit_left)[0][0]:, :]

                if reply == QMessageBox.Yes:
                    cmfgen_filename_cont = cmfgen_filename[0:-3] + 'cont'
                    cont = cmfgenplot.spectr_input(cmfgen_filename_cont)
                    f = interp1d(cont[:, 0], cont[:, 1])
                    interpolated_data = f(cmfgen_modeldata[:, 0])
                    current_plot = self.pw.plot(cmfgen_modeldata[:, 0],
                                 (cmfgen_modeldata[:, 1] / interpolated_data), pen=pg.mkColor(self.i))
                else:
                    current_plot = self.pw.plot(cmfgen_modeldata[:, 0], cmfgen_modeldata[:, 1], pen=pg.mkColor(self.i))
                plot_name = cmfgen_filename.split("/")[-3]
                self.all_plot_items[plot_name] = current_plot
                self.add_to_list_widget(plot_name)
                self.i += 2
        except IOError as exception:
            self.cmfgen_error_event(exception.message)

    def cmfgen_error_event(self,message):
        """
        Method creates window with error message, 
        when cmfgen_plot raise IOError.
        :param message: The error message.
        """
        QMessageBox.critical(self, "IOError", "Can't read CMFGEN model file\n" + message)

    def add_to_list_widget(self, name):
        """
        Add item to widget list with name
        :param name: Plot item name 
        """
        item = QListWidgetItem('%s' % name)
        item.setBackgroundColor(pg.mkColor(self.i))
        self.listWidget.addItem(item)

    def list_widget_clear_selection(self):
        """
        Clear widget list 
        """
        self.listWidget.clearSelection()

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
        self.setWindowTitle("Spectrum observer")

        self.cw = QtGui.QWidget()
        self.setCentralWidget(self.cw)
        self.l = QtGui.QHBoxLayout()
        self.cw.setLayout(self.l)


        self.init_ui()

        self.win = pg.GraphicsWindow()
        self.pw = self.win.addPlot()
        self.pw.showGrid(x=True, y=True)
        self.l.addWidget(self.win)

        self.i = 0
        self.all_plot_items = {}

    def init_ui(self):
        """
        Buttons and widgets init
        """
        self.title = QtGui.QPushButton('Unselect all plots', self)
        self.title.clicked.connect(self.list_widget_clear_selection)
        self.title.setFixedWidth(150)
        horizontalLayout = QtGui.QVBoxLayout()
        horizontalLayout.addWidget(self.title)

        self.listWidget = QListWidget()
        self.listWidget.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)

        self.listWidget.setFixedHeight(175)
        self.listWidget.setFixedWidth(150)
        horizontalLayout.addWidget(self.listWidget)

        horizontalLayout.addStretch()
        self.l.addLayout(horizontalLayout)

        open_file = QAction('Open from Table', self)
        open_file.setStatusTip('Open new File')
        open_file.triggered.connect(self.table_plot)

        load_lines = QAction('Load Lines', self)
        load_lines.setStatusTip('Load some Line')
        load_lines.triggered.connect(self.load_lines)

        clear_plot = QAction('Clear', self)
        clear_plot.setStatusTip('Clear plot')
        clear_plot.triggered.connect(self.clear_plot)

        cmf_plot = QAction('Open from CMFGEN', self)
        cmf_plot.setStatusTip('CMFGEN plot')
        cmf_plot.triggered.connect(self.cmfgen_plot)

        fits_plot = QAction('Open from FITS', self)
        fits_plot.setStatusTip('CMFGEN plot')
        fits_plot.triggered.connect(self.fits_plot)

        menu_bar = self.menuBar()
        menu_bar.addAction(fits_plot)
        menu_bar.addAction(open_file)
        menu_bar.addAction(cmf_plot)
        menu_bar.addAction(load_lines)
        menu_bar.addAction(clear_plot)


app = QtGui.QApplication(sys.argv)
main = MainWindow()
main.show()
sys.exit(app.exec_())
