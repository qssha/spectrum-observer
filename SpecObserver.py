#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import numpy as np
from PyQt4.QtGui import QMainWindow, QApplication, QHBoxLayout, QAbstractItemView, QWidget, QVBoxLayout
from PyQt4.QtGui import QAction, QPushButton, QListWidget, QListWidgetItem, QLabel, QInputDialog
from PyQt4.QtGui import QFileDialog
from PyQt4.QtGui import QIcon
from PyQt4.QtGui import QMessageBox
from PyQt4 import QtCore
from PyAstronomy import pyasl
from pyqtgraph import GraphicsWindow, mkColor, InfiniteLine, SignalProxy

import CmfgenParse
import CustomExporter


class SpecObserver(QMainWindow):
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
                wave, flux = pyasl.read1dFitsSpec(fits_file)
                current_plot = self.pw.plot(wave, flux, pen=mkColor(self.i))
                plot_name = fits_file.split("/")[-1]
                self.all_plot_items[plot_name] = current_plot
                self.all_fits_paths[plot_name] = fits_file
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
        reply = QMessageBox.question(self, 'Message',
                                           "Are you sure to quit?", QMessageBox.Yes |
                                           QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
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
                line = InfiniteLine(pos=float(lines_data[i, 0]), label=lines_data[i, 1],
                                       labelOpts={'position': line_label_position, 'color': mkColor("w")},
                                       name=lines_data[i, 1])
                line.setPen(style=QtCore.Qt.DotLine)
                self.pw.addItem(line)
                self.all_lines.append([float(lines_data[i, 0]), lines_data[i, 1]])

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
                dt = max(data[1:, 0] - data[0:-1,  0])
                binned_data, dt = pyasl.binningx0dt(data[:, 0], data[:, 1], x0=min(data[:, 0]), dt=dt)
                current_plot = self.pw.plot(binned_data[:, 0], binned_data[:, 1], pen=mkColor(self.i))
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
        self.all_point_items = {}
        self.all_fits_paths = {}
        self.all_lines = []
        self.listWidget.clear()
        self.listPointWidget.clear()

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
                reply = QMessageBox.question(self, 'Message', "Do you want to plot normalized spectrum from *cont file?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

                x_limit_left = 3800
                x_limit_right = 8000

                cmfgen_modeldata = CmfgenParse.spectr_input(cmfgen_filename)
                cmfgen_modeldata = cmfgen_modeldata[:np.where(cmfgen_modeldata[:, 0] < x_limit_right)[0][-1], :]
                cmfgen_modeldata = cmfgen_modeldata[np.where(cmfgen_modeldata[:, 0] > x_limit_left)[0][0]:, :]

                dt = max(cmfgen_modeldata[1:, 0] - cmfgen_modeldata[0:-1, 0])
                cmfgen_binned_data, dt = pyasl.binningx0dt(cmfgen_modeldata[:, 0], cmfgen_modeldata[:, 1],
                                                           x0=min(cmfgen_modeldata[:, 0]), dt=dt)
                if reply == QMessageBox.Yes:
                    cmfgen_filename_cont = cmfgen_filename[0:-3] + 'cont'
                    cont = CmfgenParse.spectr_input(cmfgen_filename_cont)
                    interpolated_data = pyasl.intep(cont[:, 0], cont[:, 1], cmfgen_binned_data[:, 0])
                    current_plot = self.pw.plot(cmfgen_binned_data[:, 0],
                                 (cmfgen_binned_data[:, 1] / interpolated_data), pen=mkColor(self.i))
                else:
                    current_plot = self.pw.plot(cmfgen_binned_data[:, 0], cmfgen_binned_data[:, 1], pen=mkColor(self.i))
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
        # print(self.all_plot_items[unicode(item.text())].getData())
        item.setBackgroundColor(mkColor(self.i))
        self.listWidget.addItem(item)

    def list_widget_clear_selection(self):
        """
        Clear widget list 
        """
        self.listWidget.clearSelection()

    def mouse_moved(self, evt):
        """
        Call for mouse move event
        :param evt Mouse event: 
        """
        self.mouse_point = self.pw.vb.mapSceneToView(evt[0])
        self.label.setText("x = %0.2f, y = %0.2e" % (
            self.mouse_point.x(), self.mouse_point.y()))

    def remove_selected_plots(self):
        """
        Remove selected items from listWidget from plot, listWidget
         and all_plot_items dictionary.
        """
        for selected_item in self.listWidget.selectedItems():
            name = unicode(selected_item.text())
            self.pw.removeItem(self.all_plot_items[name])
            self.all_plot_items.pop(name)
            self.listWidget.takeItem(self.listWidget.row(selected_item))

    def export_selected_plots(self):
        """
        Choose directory and save all selectes items as tables
        """
        if len(self.listWidget.selectedItems()) != 1:
            self.single_plot_warning_event()
            return

        export_name = unicode(QFileDialog.getSaveFileName(self, "Select Export Directory and Name"))
        if export_name != '':
            name = unicode(self.listWidget.selectedItems()[0].text())
            export_name += ".data"
            np.savetxt(export_name, np.transpose(self.all_plot_items[name].getData()))

    def add_to_list_point_widget(self, event):
        """
        Add point when clicked on graphics scene with Control.
        :param event: Mouse event
        :return: 
        """
        if event.modifiers() == QtCore.Qt.ControlModifier:
            x = np.array([self.mouse_point.x()])
            y = np.array([self.mouse_point.y()])
            name = "x = %0.2f, y = %0.4e" % (self.mouse_point.x(), self.mouse_point.y())
            current_point = self.pw.plot(x, y, pen=None, symbol='t', symbolPen=None, symbolSize=10,
                                         symbolBrush=mkColor(5))
            self.all_point_items[name] = current_point
            item = QListWidgetItem('%s' % name)
            self.listPointWidget.addItem(item)

    def remove_selected_points(self):
        """
        Remove selected points from listPointWidget
        :return: 
        """
        for selected_item in self.listPointWidget.selectedItems():
            name = unicode(selected_item.text())

            self.pw.removeItem(self.all_point_items[name])
            self.all_point_items.pop(name)
            self.listPointWidget.takeItem(self.listPointWidget.row(selected_item))

    def list_point_widget_clear_selection(self):
        """
        Clear point widget list 
        """
        self.listPointWidget.clearSelection()

    def calculate_flux_for_selected_plots(self):
        """
        Rescale selected plots from distance in kpc
        :return: 
        """
        text, ok = QInputDialog.getText(self, 'Rescale fluxes from distance', 'Rescaling fluxes to 1 kpc.\n'
                                                                              'Enter distance to object(s) in kpc,'
                                                                              ' for example, 3 or 2.3 * 10** 3')
        try:
            if text != '' and ok is True:
                distance = eval(str(text))
                for selected_item in self.listWidget.selectedItems():
                    name = unicode(selected_item.text())
                    data = np.transpose(self.all_plot_items[name].getData())
                    data[:, 1] = data[:, 1] * distance**2
                    self.all_plot_items[name].setData(data)
                    self.pw.autoRange()
        except NameError as exception:
            self.name_error_event(exception.message)

    def smooth_selected_plots(self):
        """
        Smooth selected plots
        :return: 
        """
        text, ok = QInputDialog.getText(self, 'Data smoothing', 'Enter smoothing window, Angstrom:')
        try:
            if text != '' and ok is True:
                window_length = eval(str(text))
                for selected_item in self.listWidget.selectedItems():
                    name = unicode(selected_item.text())
                    data = np.transpose(self.all_plot_items[name].getData())
                    window_length_cell = int(window_length / max(data[1:, 0] - data[0:-1, 0]))
                    if window_length_cell % 2 == 0: window_length_cell += 1
                    data[:, 1] = pyasl.smooth(data[:, 1], window_length_cell, 'hamming')
                    self.all_plot_items[name].setData(data)
        except NameError and ValueError as exception:
            self.name_error_event(exception.message)

    def unred_selected_plots(self):
        """
        Unred selected plots from astrolib IDL
        :return: 
        """
        text, ok = QInputDialog.getText(self, 'Deredden flux', 'Deredden a flux vector. Enter Av:')
        try:
            if text != '' and ok is True:
                a_v = eval(str(text))
                for selected_item in self.listWidget.selectedItems():
                    name = unicode(selected_item.text())
                    data = np.transpose(self.all_plot_items[name].getData())
                    data[:, 1] = pyasl.unred(data[:,0], data[:,1], ebv=a_v/3.2)
                    self.all_plot_items[name].setData(data)
        except NameError as exception:
            self.name_error_event(exception.message)

    def calculate_red_shift_for_selected_plots(self):
        """
        Calculate red shift from z
        :return: 
        """
        text, ok = QInputDialog.getText(self, 'Rescale wavelength from z', 'Enter z')
        try:
            if text != '' and ok is True:
                z = eval(str(text))
                for selected_item in self.listWidget.selectedItems():
                    name = unicode(selected_item.text())
                    data = np.transpose(self.all_plot_items[name].getData())
                    data[:, 0] = data[:, 0] * (1 + z)
                    self.all_plot_items[name].setData(data)
        except NameError as exception:
            self.name_error_event(exception.message)

    def calculate_continuum_for_selected_plots(self):
        """
        Calculate continuum for selected plots from all points
        :return: 
        """
        for selected_item in self.listWidget.selectedItems():
            name = unicode(selected_item.text())
            data = np.transpose(self.all_plot_items[name].getData())

            point_data = []
            for index in range(self.listPointWidget.count()):
                point_name = unicode(self.listPointWidget.item(index).text())
                point_data.append([self.all_point_items[point_name].getData()[0][0],
                             self.all_point_items[point_name].getData()[1][0]])
                self.pw.removeItem(self.all_point_items[point_name])

            point_data = np.array(point_data)
            data = data[:np.where(data[:, 0] < np.max(point_data[:, 0]))[0][-1], :]
            data = data[np.where(data[:, 0] > np.min(point_data[:, 0]))[0][0]:, :]

            interpolated_cont = pyasl.intep(point_data[:, 0], point_data[:, 1], data[:, 0])

            data[:, 1] = data[:, 1] / interpolated_cont
            self.all_plot_items[name].setData(data)
            self.listPointWidget.clear()
            self.pw.autoRange()

    def calculate_fwhm_for_intervals(self):
        """
        Caclculate fwhm for lines between points
        :return: 
        """

    def name_error_event(self,message):
        """
        Method creates window with error message, 
        when program can't evaluate input string
        :param message: The error message.
        """
        QMessageBox.critical(self, "IOError", "Can't evaluate input string\n" + message)

    def export_matplotlib(self):
        """
        Export with lines to Matplotlib
        :return: 
        """
        exporter = CustomExporter.CustomMatplotlib(self.pw)
        exporter.export(self.all_lines)

    def export_as_fits_for_selected_plot(self):
        """
        Export spectrum as FITS
        """
        if len(self.listWidget.selectedItems()) != 1:
            self.single_plot_warning_event()
            return

        export_name = unicode(QFileDialog.getSaveFileName(self, "Select Export Directory and Name"))
        if export_name != '':
            name = unicode(self.listWidget.selectedItems()[0].text())
            data = np.transpose(self.all_plot_items[name].getData())
            if name in self.all_fits_paths:
                pyasl.write1dFitsSpec(export_name + ".fits", data[:, 1], wvl=data[:, 0],
                                      refFileName=self.all_fits_paths[name], clobber=True)
            else:
                pyasl.write1dFitsSpec(export_name + ".fits", data[:, 1], wvl=data[:, 0], clobber=True)

    def change_selected_plot_name(self):
        """
        Change name of selected plot
        :return: 
        """
        if len(self.listWidget.selectedItems()) != 1:
            self.single_plot_warning_event()
            return

        text, ok = QInputDialog.getText(self, 'Plot rename', 'Choose new name for plot')
        if text != '' and ok is True:
            name = unicode(self.listWidget.selectedItems()[0].text())
            self.all_plot_items[unicode(text)] = self.all_plot_items[name]
            self.all_plot_items.pop(name)
            self.listWidget.selectedItems()[0].setText(unicode(text));


    def single_plot_warning_event(self):
        """
        Method creates window with warning message, when more than single plot chosen
        """
        QMessageBox.warning(self, "Warning", "Please choose one plot\n")

    def __init__(self):
        """
        Инициализируем окно. Добавляем иконку.
        Создаем виджет для графики. Добавляем туда PlotWidget.
        """
        QMainWindow.__init__(self)
        self.setWindowIcon(QIcon("web.png"))
        self.setWindowTitle("Spectrum observer")

        self.cw = QWidget()
        self.setCentralWidget(self.cw)
        self.l = QHBoxLayout()
        self.cw.setLayout(self.l)

        self.win = GraphicsWindow()
        self.pw = self.win.addPlot()
        self.pw.showGrid(x=True, y=True)

        self.init_ui()
        self.l.addWidget(self.win)

        self.i = 0
        self.all_plot_items = {}
        self.all_point_items = {}
        self.all_lines = []
        self.all_fits_paths = {}

    def init_ui(self):
        """
        Buttons and widgets init
        """
        self.vertical_layout = QVBoxLayout()

        self.unselect = QPushButton('Unselect all plots', self)
        self.unselect.clicked.connect(self.list_widget_clear_selection)
        self.unselect.setFixedWidth(170)

        self.change_name = QPushButton('Rename', self)
        self.change_name.clicked.connect(self.change_selected_plot_name)
        self.change_name.setFixedWidth(85)

        self.remove = QPushButton('Remove', self)
        self.remove.clicked.connect(self.remove_selected_plots)
        self.remove.setFixedWidth(85)

        self.listWidget = QListWidget()
        self.listWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.listWidget.setFixedHeight(125)
        self.listWidget.setFixedWidth(170)

        self.horizontal_first = QHBoxLayout()
        self.horizontal_first.addWidget(self.remove)
        self.horizontal_first.addWidget(self.change_name)

        self.label = QLabel()
        self.proxy = SignalProxy(self.pw.scene().sigMouseMoved, rateLimit=3, slot=self.mouse_moved)

        self.pw.scene().sigMouseClicked.connect(self.add_to_list_point_widget)

        self.unselect_points = QPushButton('Unselect all points', self)
        self.unselect_points.clicked.connect(self.list_point_widget_clear_selection)
        self.unselect_points.setFixedWidth(170)

        self.listPointWidget = QListWidget()
        self.listPointWidget.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.listPointWidget.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.listPointWidget.setFixedHeight(150)
        self.listPointWidget.setFixedWidth(170)

        self.remove_points = QPushButton('Remove point(s)', self)
        self.remove_points.clicked.connect(self.remove_selected_points)
        self.remove_points.setFixedWidth(170)

        self.horizontal_second = QHBoxLayout()
        self.calculate_flux = QPushButton('Distance', self)
        self.calculate_flux.clicked.connect(self.calculate_flux_for_selected_plots)
        self.calculate_flux.setFixedWidth(85)
        self.calculate_redshift = QPushButton('Red shift', self)
        self.calculate_redshift.clicked.connect(self.calculate_red_shift_for_selected_plots)
        self.calculate_redshift.setFixedWidth(85)

        self.horizontal_second.addWidget(self.calculate_flux)
        self.horizontal_second.addWidget(self.calculate_redshift)

        self.horizontal_third = QHBoxLayout()
        self.calculate_smooth = QPushButton('Smooth', self)
        self.calculate_smooth.clicked.connect(self.smooth_selected_plots)
        self.calculate_smooth.setFixedWidth(85)
        self.calculate_unred = QPushButton('Unred', self)
        self.calculate_unred.clicked.connect(self.unred_selected_plots)
        self.calculate_unred.setFixedWidth(85)

        self.horizontal_third.addWidget(self.calculate_smooth)
        self.horizontal_third.addWidget(self.calculate_unred)

        self.horizontal_fourth = QHBoxLayout()
        self.calculate_continuum = QPushButton('Continuum', self)
        self.calculate_continuum.clicked.connect(self.calculate_continuum_for_selected_plots)
        self.calculate_continuum.setFixedWidth(85)
        self.calculate_fwhm = QPushButton('FWHM', self)
        self.calculate_fwhm.clicked.connect(self.calculate_fwhm_for_intervals)
        self.calculate_fwhm.setFixedWidth(85)

        self.horizontal_fourth.addWidget(self.calculate_continuum)
        self.horizontal_fourth.addWidget(self.calculate_fwhm)

        self.export_to_matplotlib = QPushButton('Export to eps/pdf', self)
        self.export_to_matplotlib.clicked.connect(self.export_matplotlib)
        self.export_to_matplotlib.setFixedWidth(170)

        self.horizontal_fifth = QHBoxLayout()
        self.fits_export = QPushButton('Export FITS', self)
        self.fits_export.clicked.connect(self.export_as_fits_for_selected_plot)
        self.fits_export.setFixedWidth(85)
        self.export = QPushButton('Export', self)
        self.export.clicked.connect(self.export_selected_plots)
        self.export.setFixedWidth(85)
        self.horizontal_fifth.addWidget(self.fits_export)
        self.horizontal_fifth.addWidget(self.export)

        self.vertical_layout.addWidget(self.unselect)
        self.vertical_layout.addWidget(self.listWidget)
        self.vertical_layout.addLayout(self.horizontal_first)
        self.vertical_layout.addLayout(self.horizontal_fifth)
        self.vertical_layout.addLayout(self.horizontal_second)
        self.vertical_layout.addLayout(self.horizontal_third)
        self.vertical_layout.addLayout(self.horizontal_fourth)
        self.vertical_layout.addWidget(self.unselect_points)
        self.vertical_layout.addWidget(self.listPointWidget)
        self.vertical_layout.addWidget(self.remove_points)
        self.vertical_layout.addWidget(self.export_to_matplotlib)
        self.vertical_layout.addStretch()
        self.vertical_layout.addWidget(self.label)

        self.l.addLayout(self.vertical_layout)

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


app = QApplication(sys.argv)
main = SpecObserver()
main.show()
sys.exit(app.exec_())
