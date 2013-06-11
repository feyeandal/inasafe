# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'batch_runner_base.ui'
#
# Created: Tue Jun 11 14:31:25 2013
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
        BatchRunnerBase.setWindowModality(QtCore.Qt.ApplicationModal)
        BatchRunnerBase.resize(553, 483)
        self.gridLayout = QtGui.QGridLayout(BatchRunnerBase)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.label = QtGui.QLabel(BatchRunnerBase)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName(_fromUtf8("label"))
        self.horizontalLayout_2.addWidget(self.label)
        self.leSourcePath = QtGui.QLineEdit(BatchRunnerBase)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.leSourcePath.sizePolicy().hasHeightForWidth())
        self.leSourcePath.setSizePolicy(sizePolicy)
        self.leSourcePath.setObjectName(_fromUtf8("leSourcePath"))
        self.horizontalLayout_2.addWidget(self.leSourcePath)
        self.tbBrowse = QtGui.QToolButton(BatchRunnerBase)
        self.tbBrowse.setObjectName(_fromUtf8("tbBrowse"))
        self.horizontalLayout_2.addWidget(self.tbBrowse)
        self.gridLayout.addLayout(self.horizontalLayout_2, 0, 0, 1, 1)
        self.lvTask = QtGui.QListView(BatchRunnerBase)
        self.lvTask.setMinimumSize(QtCore.QSize(450, 0))
        self.lvTask.setObjectName(_fromUtf8("lvTask"))
        self.gridLayout.addWidget(self.lvTask, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(BatchRunnerBase)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Close|QtGui.QDialogButtonBox.Ok|QtGui.QDialogButtonBox.Open)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)

        self.retranslateUi(BatchRunnerBase)
        QtCore.QMetaObject.connectSlotsByName(BatchRunnerBase)

    def retranslateUi(self, BatchRunnerBase):
        BatchRunnerBase.setWindowTitle(_translate("BatchRunnerBase", "InaSAFE Batch Runner", None))
        self.label.setText(_translate("BatchRunnerBase", "Scenarios directory", None))
        self.tbBrowse.setText(_translate("BatchRunnerBase", "...", None))

