"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Path Line Edit widget.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
import logging
from PyQt4.QtGui import QWidget, QFileDialog
from safe_qgis.path_line_edit_base import Ui_PathLineEditBase
LOGGER = logging.getLogger('InaSAFE')


class PathLineEdit(QWidget, Ui_PathLineEditBase):
    def __init__(self, theParent=None):
        QWidget.__init__(self, theParent)
        self.setupUi(self)
        self.tbBrowse.clicked.connect(self.browseClicked)
        LOGGER.info('Path Line Edit widget initialised')

    def setText(self, theValue):
        self.lePath.setText(theValue)

    def text(self):
        return self.lePath.text()

    def browseClicked(self):
        """ Show a directory selection dialog.
        This function will show the dialog then set theLineEdit widget
        text with output from the dialog.
        """
        LOGGER.info('browse clicked')
        myPath = self.lePath.text()
        myTitle = self.tr('Choose directory')
        myNewPath = QFileDialog.getExistingDirectory(
            self,
            myTitle,
            myPath,
            QFileDialog.ShowDirsOnly)

        if not myNewPath:
            return

        self.lePath.setText(myNewPath)
