# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'batch_options_base.ui'
#
# Created: Wed Jun 12 11:44:37 2013
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

class Ui_BatchOptionsBase(object):
    def setupUi(self, BatchOptionsBase):
        BatchOptionsBase.setObjectName(_fromUtf8("BatchOptionsBase"))
        BatchOptionsBase.resize(400, 241)
        self.gridLayout = QtGui.QGridLayout(BatchOptionsBase)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.groupBox = QtGui.QGroupBox(BatchOptionsBase)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout_2 = QtGui.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.cbIgnoreDataPath = QtGui.QCheckBox(self.groupBox)
        self.cbIgnoreDataPath.setObjectName(_fromUtf8("cbIgnoreDataPath"))
        self.gridLayout_2.addWidget(self.cbIgnoreDataPath, 0, 0, 1, 1)
        self.pleDataPath = QtGui.QLineEdit(self.groupBox)
        self.pleDataPath.setObjectName(_fromUtf8("pleDataPath"))
        self.gridLayout_2.addWidget(self.pleDataPath, 1, 0, 1, 1)
        self.tbBrowse = QtGui.QToolButton(self.groupBox)
        self.tbBrowse.setObjectName(_fromUtf8("tbBrowse"))
        self.gridLayout_2.addWidget(self.tbBrowse, 1, 1, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)
        self.groupBox_2 = QtGui.QGroupBox(BatchOptionsBase)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.gridLayout_3 = QtGui.QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName(_fromUtf8("gridLayout_3"))
        self.pleReportPath = QtGui.QLineEdit(self.groupBox_2)
        self.pleReportPath.setObjectName(_fromUtf8("pleReportPath"))
        self.gridLayout_3.addWidget(self.pleReportPath, 0, 0, 1, 1)
        self.tbBrowse_2 = QtGui.QToolButton(self.groupBox_2)
        self.tbBrowse_2.setObjectName(_fromUtf8("tbBrowse_2"))
        self.gridLayout_3.addWidget(self.tbBrowse_2, 0, 1, 1, 1)
        self.gridLayout.addWidget(self.groupBox_2, 1, 0, 1, 1)
        self.buttonBox = QtGui.QDialogButtonBox(BatchOptionsBase)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.gridLayout.addWidget(self.buttonBox, 2, 0, 1, 1)

        self.retranslateUi(BatchOptionsBase)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), BatchOptionsBase.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), BatchOptionsBase.reject)
        QtCore.QMetaObject.connectSlotsByName(BatchOptionsBase)

    def retranslateUi(self, BatchOptionsBase):
        BatchOptionsBase.setWindowTitle(_translate("BatchOptionsBase", "Dialog", None))
        self.groupBox.setTitle(_translate("BatchOptionsBase", "Default Data Directory", None))
        self.cbIgnoreDataPath.setText(_translate("BatchOptionsBase", "Ignore custom data path in scenario files", None))
        self.tbBrowse.setText(_translate("BatchOptionsBase", "...", None))
        self.groupBox_2.setTitle(_translate("BatchOptionsBase", "Output Report Directory", None))
        self.tbBrowse_2.setText(_translate("BatchOptionsBase", "...", None))

