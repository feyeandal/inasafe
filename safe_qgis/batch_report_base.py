# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'batch_report_base.ui'
#
# Created: Thu Feb 28 16:17:55 2013
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_BatchReportBase(object):
    def setupUi(self, BatchReportBase):
        BatchReportBase.setObjectName(_fromUtf8("BatchReportBase"))
        BatchReportBase.resize(830, 620)
        self.buttonBox = QtGui.QDialogButtonBox(BatchReportBase)
        self.buttonBox.setGeometry(QtCore.QRect(430, 540, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.columnView = QtGui.QColumnView(BatchReportBase)
        self.columnView.setGeometry(QtCore.QRect(40, 60, 551, 291))
        self.columnView.setObjectName(_fromUtf8("columnView"))

        self.retranslateUi(BatchReportBase)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), BatchReportBase.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), BatchReportBase.reject)
        QtCore.QMetaObject.connectSlotsByName(BatchReportBase)

    def retranslateUi(self, BatchReportBase):
        BatchReportBase.setWindowTitle(QtGui.QApplication.translate("BatchReportBase", "Dialog", None, QtGui.QApplication.UnicodeUTF8))

