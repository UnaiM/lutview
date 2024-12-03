import functools

import numpy
from PySide6 import QtCore, QtGraphs, QtGraphsWidgets, QtQuickWidgets


class CubeView(QtQuickWidgets.QQuickWidget):

    SIZE = 20

    def __init__(self):
        super().__init__()
        self.scatter = QtGraphsWidgets.Q3DScatterWidgetItem()
        self.scatter.setWidget(self)
        self.series = QtGraphs.QScatter3DSeries()
        self.scatter.addSeries(self.series)
    
    def load(self, processor):
        array = uniform_samples(self.SIZE)
        cpu_proc = processor.getDefaultCPUProcessor()
        array = array.flatten()
        cpu_proc.applyRGB(array)
        array.resize((self.SIZE ** 3, 3))
        self.series.setDataArray(tuple(QtGraphs.QScatterDataItem(*x) for x in array))


class _CubeThread(QtCore.QThread):

    add = QtCore.Signal()


@functools.lru_cache(maxsize=4)
def uniform_samples(size):
    axis = numpy.linspace(0, 1, size, dtype=numpy.float32)
    mx, my, mz = numpy.meshgrid(axis, axis, axis)
    # no idea why, but ZXY gives the expected ordering.
    return numpy.dstack((mz.flat, mx.flat, my.flat))[0]
