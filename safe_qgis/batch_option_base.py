# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'batch_option_base.ui'
#
# Created: Mon Mar 18 16:10:17 2013
#      by: PyQt4 UI code generator 4.8.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_BatchOptionBase(object):
    def setupUi(self, BatchOptionBase):
        BatchOptionBase.setObjectName(_fromUtf8("BatchOptionBase"))
        BatchOptionBase.resize(400, 241)
        self.verticalLayout = QtGui.QVBoxLayout(BatchOptionBase)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(BatchOptionBase)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.cbIgnoreDataPath = QtGui.QCheckBox(self.groupBox)
        self.cbIgnoreDataPath.setObjectName(_fromUtf8("cbIgnoreDataPath"))
        self.verticalLayout_2.addWidget(self.cbIgnoreDataPath)
        self.pleDataPath = PathLineEdit(self.groupBox)
        self.pleDataPath.setObjectName(_fromUtf8("pleDataPath"))
        self.verticalLayout_2.addWidget(self.pleDataPath)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(BatchOptionBase)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.groupBox_2)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.pleReportPath = PathLineEdit(self.groupBox_2)
        self.pleReportPath.setObjectName(_fromUtf8("pleReportPath"))
        self.verticalLayout_3.addWidget(self.pleReportPath)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.buttonBox = QtGui.QDialogButtonBox(BatchOptionBase)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(BatchOptionBase)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), BatchOptionBase.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), BatchOptionBase.reject)
        QtCore.QMetaObject.connectSlotsByName(BatchOptionBase)

    def retranslateUi(self, BatchOptionBase):
        BatchOptionBase.setWindowTitle(QtGui.QApplication.translate("BatchOptionBase", "Dialog", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("BatchOptionBase", "Default Data Directory", None, QtGui.QApplication.UnicodeUTF8))
        self.cbIgnoreDataPath.setText(QtGui.QApplication.translate("BatchOptionBase", "Ignore custom data path in scenario files", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox_2.setTitle(QtGui.QApplication.translate("BatchOptionBase", "Output Report Directory", None, QtGui.QApplication.UnicodeUTF8))

from safe_qgis.path_line_edit import PathLineEdit
