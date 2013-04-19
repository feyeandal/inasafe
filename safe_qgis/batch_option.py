"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Batch option dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'bungcip@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '01/10/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import sys
import logging

from PyQt4.QtGui import (QDialog, QFileDialog, QTableWidgetItem, QMessageBox)


from safe_qgis.batch_option_base import Ui_BatchOptionBase
from safe_qgis.path_line_edit import PathLineEdit

LOGGER = logging.getLogger('InaSAFE')


class BatchOption(QDialog, Ui_BatchOptionBase):
    """Script Dialog for InaSAFE."""

    def __init__(self, theParent=None):
        """Constructor for the dialog.

        Args:
           theParent - Optional widget to use as parent.
        Returns:
           not applicable
        Raises:
           no exceptions explicitly raised
        """
        QDialog.__init__(self, theParent)
        self.setupUi(self)

    @staticmethod
    def getOptions(theDataPath='', theReportPath='', theIgnoreDataPath=False):
        """Get options value from dialog.
        The returned value is tuple with this format:
          (data_path: str, report_path: str, ignore_data_path: bool)

        Params:
            * theDataPath - default value for data path
            * theReportPath - default value for report path
            * theIgnoreDataPath - default value for ignore data path

        Returns:
            A tuple when 'OK' button is pressed, false otherwise
        """

        myDialog = BatchOption()

        # set default value
        myDialog.pleDataPath.setText(theDataPath)
        myDialog.pleReportPath.setText(theReportPath)
        myDialog.cbIgnoreDataPath.setChecked(theIgnoreDataPath)

        myResult = myDialog.exec_()

        # return false when user press 'cancel'
        if not myResult:
            return False

        # get result
        myDataPath = myDialog.pleDataPath.text()
        myReportPath = myDialog.pleReportPath.text()
        myIgnoreDataPath = myDialog.cbIgnoreDataPath.isChecked()

        return (myDataPath, myReportPath, myIgnoreDataPath)


if __name__ == '__main__':
    from PyQt4.QtGui import QApplication
    from PyQt4.QtCore import QCoreApplication
    import sys

    QCoreApplication.setOrganizationDomain('aifdr')
    QCoreApplication.setApplicationName('inasafe')

    app = QApplication(sys.argv)
    myValue = BatchOption.getOptions()

    print myValue

    app.exec_()
