# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'path_line_edit_base.ui'
#
# Created: Mon Jun 10 11:52:52 2013
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

class Ui_PathLineEditBase(object):
    def setupUi(self, PathLineEditBase):
        PathLineEditBase.setObjectName(_fromUtf8("PathLineEditBase"))
        PathLineEditBase.resize(285, 33)
        self.gridLayout = QtGui.QGridLayout(PathLineEditBase)
        self.gridLayout.setMargin(0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.lePath = QtGui.QLineEdit(PathLineEditBase)
        self.lePath.setObjectName(_fromUtf8("lePath"))
        self.horizontalLayout.addWidget(self.lePath)
        self.tbBrowse = QtGui.QToolButton(PathLineEditBase)
        self.tbBrowse.setObjectName(_fromUtf8("tbBrowse"))
        self.horizontalLayout.addWidget(self.tbBrowse)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.retranslateUi(PathLineEditBase)
        QtCore.QMetaObject.connectSlotsByName(PathLineEditBase)

    def retranslateUi(self, PathLineEditBase):
        PathLineEditBase.setWindowTitle(_translate("PathLineEditBase", "Form", None))
        self.tbBrowse.setText(_translate("PathLineEditBase", "...", None))

