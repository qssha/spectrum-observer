from pyqtgraph import fn, QtCore, PlotItem
from PyQt4.QtGui import QMainWindow
from pyqtgraph.exporters import MatplotlibExporter
import lineid_plot
import numpy as np
from pyqtgraph.exporters.Matplotlib import MatplotlibWindow
from pyqtgraph.widgets import MatplotlibWidget


class CustomMatplotlib(MatplotlibExporter):
    def __init__(self, item):
        MatplotlibExporter.__init__(self, item)

    def parameters(self):
        super(CustomMatplotlib, self).parameters()

    def cleanAxes(self, axl):
        super(CustomMatplotlib, self).cleanAxes(axl)

    def export(self, loaded_lines, fileName=None):
        if isinstance(self.item, PlotItem):
            ak = lineid_plot.initial_annotate_kwargs()
            ak['arrowprops']['arrowstyle'] = "->"
            pk = lineid_plot.initial_plot_kwargs()


            mpw = MatplotlibWindow()
            MatplotlibExporter.windows.append(mpw)

            stdFont = 'Arial'

            fig = mpw.getFigure()

            # get labels from the graphic item
            xlabel = self.item.axes['bottom']['item'].label.toPlainText()
            ylabel = self.item.axes['left']['item'].label.toPlainText()
            title = self.item.titleLabel.text

            ax = fig.add_subplot(111, title=title)
            ax.clear()
            self.cleanAxes(ax)
            # ax.grid(True)
            for item in self.item.curves:
                x, y = item.getData()
                opts = item.opts
                pen = fn.mkPen(opts['pen'])
                if pen.style() == QtCore.Qt.NoPen:
                    linestyle = ''
                else:
                    linestyle = '-'
                color = tuple([c / 255. for c in fn.colorTuple(pen.color())])
                symbol = opts['symbol']
                if symbol == 't':
                    symbol = '^'
                symbolPen = fn.mkPen(opts['symbolPen'])
                symbolBrush = fn.mkBrush(opts['symbolBrush'])
                markeredgecolor = tuple([c / 255. for c in fn.colorTuple(symbolPen.color())])
                markerfacecolor = tuple([c / 255. for c in fn.colorTuple(symbolBrush.color())])
                markersize = opts['symbolSize']

                if opts['fillLevel'] is not None and opts['fillBrush'] is not None:
                    fillBrush = fn.mkBrush(opts['fillBrush'])
                    fillcolor = tuple([c / 255. for c in fn.colorTuple(fillBrush.color())])
                    ax.fill_between(x=x, y1=y, y2=opts['fillLevel'], facecolor=fillcolor)

                pl = ax.plot(x, y, marker=symbol, color=color, linewidth=pen.width(),
                             linestyle=linestyle, markeredgecolor=markeredgecolor, markerfacecolor=markerfacecolor,
                             markersize=markersize)
                xr, yr = self.item.viewRange()
                ax.set_xbound(*xr)
                ax.set_ybound(*yr)
                if self.item.curves.index(item) == 0:
                    line_wave = []
                    line_label1 = []

                    for line in loaded_lines:
                        if np.min(x) < line[0] < np.max(x):
                            line_wave.append(line[0])
                            line_label1.append(line[1])

                    lineid_plot.plot_line_ids(x, y, line_wave, line_label1,
                                              annotate_kwargs=ak, plot_kwargs=pk, ax=ax)
            ax.set_xlabel(xlabel)  # place the labels.
            ax.set_ylabel(ylabel)
            mpw.draw()
        else:
            raise Exception("Matplotlib export currently only works with plot items")

    MatplotlibExporter.register()

    class MatplotlibWindow(QMainWindow):
        def __init__(self):
            QMainWindow.__init__(self)
            self.mpl = MatplotlibWidget.MatplotlibWidget()
            self.setCentralWidget(self.mpl)
            self.show()

        def __getattr__(self, attr):
            return getattr(self.mpl, attr)

        def closeEvent(self, ev):
            MatplotlibExporter.windows.remove(self)
