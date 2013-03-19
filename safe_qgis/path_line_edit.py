"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Path Line Edit widget.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

from PyQt4.QtGui import (QWidget, QHBoxLayout, QSizePolicy,
                         QLineEdit, QToolButton, QFileDialog)


class PathLineEdit(QWidget):
    def __init__(self, theParent=None):
        QWidget.__init__(self, theParent)
        self.initUi()

    def initUi(self):

        self.layout = QHBoxLayout(self)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setLayout(self.layout)

        self.lePath = QLineEdit(self)
        self.layout.addWidget(self.lePath)

        self.tbBrowse = QToolButton(self)
        self.tbBrowse.setText('...')
        self.layout.addWidget(self.tbBrowse)

        self.tbBrowse.clicked.connect(self.showDirectoryDialog)

    def setText(self, theValue):
        self.lePath.setText(theValue)

    def text(self):
        return self.lePath.text()

    def showDirectoryDialog(self):
        """ Show a directory selection dialog.
        This function will show the dialog then set theLineEdit widget
        text with output from the dialog.
        """

        myPath = self.lePath.text()
        myTitle = self.tr('Choose directory')
        myNewPath = QFileDialog.getExistingDirectory(
            self,
            myTitle,
            myPath,
            QFileDialog.ShowDirsOnly)
        self.lePath.setText(myNewPath)
