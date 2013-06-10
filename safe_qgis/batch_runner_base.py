# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'batch_runner_base.ui'
#
# Created: Mon Jun 10 17:33:14 2013
#      by: PyQt4 UI code generator 4.10
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_BatchRunnerBase(object):
    def setupUi(self, BatchRunnerBase):
        BatchRunnerBase.setObjectName(_fromUtf8("BatchRunnerBase"))
        BatchRunnerBase.resize(468, 519)
        self.gridLayout = QtGui.QGridLayout(BatchRunnerBase)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(BatchRunnerBase)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.leSourcePath = QtGui.QLineEdit(BatchRunnerBase)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.leSourcePath.sizePolicy().hasHeightForWidth())
        self.leSourcePath.setSizePolicy(sizePolicy)
        self.leSourcePath.setObjectName(_fromUtf8("leSourcePath"))
        self.gridLayout.addWidget(self.leSourcePath, 0, 1, 1, 1)
        self.tbBrowse = QtGui.QToolButton(BatchRunnerBase)
        self.tbBrowse.setObjectName(_fromUtf8("tbBrowse"))
        self.gridLayout.addWidget(self.tbBrowse, 0, 2, 1, 1)
        self.lvTask = QtGui.QListView(BatchRunnerBase)
        self.lvTask.setMinimumSize(QtCore.QSize(450, 0))
        self.lvTask.setObjectName(_fromUtf8("lvTask"))
        self.gridLayout.addWidget(self.lvTask, 1, 0, 1, 3)
        self.pbnRunAll = QtGui.QPushButton(BatchRunnerBase)
        self.pbnRunAll.setObjectName(_fromUtf8("pbnRunAll"))
        self.gridLayout.addWidget(self.pbnRunAll, 2, 0, 1, 1)
        self.pbnOption = QtGui.QPushButton(BatchRunnerBase)
        self.pbnOption.setCheckable(False)
        self.pbnOption.setChecked(False)
        self.pbnOption.setObjectName(_fromUtf8("pbnOption"))
        self.gridLayout.addWidget(self.pbnOption, 2, 1, 1, 2)

        self.retranslateUi(BatchRunnerBase)
        QtCore.QMetaObject.connectSlotsByName(BatchRunnerBase)

    def retranslateUi(self, BatchRunnerBase):
        BatchRunnerBase.setWindowTitle(_translate("BatchRunnerBase", "InaSAFE Batch Runner", None))
        self.label.setText(_translate("BatchRunnerBase", "Base path", None))
        self.tbBrowse.setText(_translate("BatchRunnerBase", "...", None))
        self.pbnRunAll.setText(_translate("BatchRunnerBase", "Run All", None))
        self.pbnOption.setText(_translate("BatchRunnerBase", "Options", None))

