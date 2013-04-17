# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'batch_runner_base.ui'
#
# Created: Wed Apr 17 10:12:41 2013
#      by: PyQt4 UI code generator 4.9
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_BatchRunnerBase(object):
    def setupUi(self, BatchRunnerBase):
        BatchRunnerBase.setObjectName(_fromUtf8("BatchRunnerBase"))
        BatchRunnerBase.resize(864, 519)
        self.gridLayout = QtGui.QGridLayout(BatchRunnerBase)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.lvTask = QtGui.QListView(BatchRunnerBase)
        self.lvTask.setObjectName(_fromUtf8("lvTask"))
        self.gridLayout.addWidget(self.lvTask, 1, 0, 1, 2)
        self.label = QtGui.QLabel(BatchRunnerBase)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.pbnOption = QtGui.QPushButton(BatchRunnerBase)
        self.pbnOption.setCheckable(False)
        self.pbnOption.setChecked(False)
        self.pbnOption.setObjectName(_fromUtf8("pbnOption"))
        self.gridLayout.addWidget(self.pbnOption, 2, 1, 1, 1)
        self.pbnRunAll = QtGui.QPushButton(BatchRunnerBase)
        self.pbnRunAll.setObjectName(_fromUtf8("pbnRunAll"))
        self.gridLayout.addWidget(self.pbnRunAll, 2, 0, 1, 1)
        self.pleSourcePath = PathLineEdit(BatchRunnerBase)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pleSourcePath.sizePolicy().hasHeightForWidth())
        self.pleSourcePath.setSizePolicy(sizePolicy)
        self.pleSourcePath.setObjectName(_fromUtf8("pleSourcePath"))
        self.gridLayout.addWidget(self.pleSourcePath, 0, 1, 1, 1)

        self.retranslateUi(BatchRunnerBase)
        QtCore.QMetaObject.connectSlotsByName(BatchRunnerBase)

    def retranslateUi(self, BatchRunnerBase):
        BatchRunnerBase.setWindowTitle(QtGui.QApplication.translate("BatchRunnerBase", "InaSAFE Batch Runner", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("BatchRunnerBase", "Base Path:", None, QtGui.QApplication.UnicodeUTF8))
        self.pbnOption.setText(QtGui.QApplication.translate("BatchRunnerBase", "Option", None, QtGui.QApplication.UnicodeUTF8))
        self.pbnRunAll.setText(QtGui.QApplication.translate("BatchRunnerBase", "Run All", None, QtGui.QApplication.UnicodeUTF8))

from safe_qgis.path_line_edit import PathLineEdit
