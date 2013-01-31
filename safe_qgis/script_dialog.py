"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Script runner dialog.**

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

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSignature
from script_dialog_base import Ui_ScriptDialogBase

import qgis

LOGGER = logging.getLogger('InaSAFE')


class ScriptDialog(QtGui.QDialog, Ui_ScriptDialogBase):
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
        QtGui.QDialog.__init__(self, theParent)
        self.setupUi(self)
        self.setWindowTitle(self.tr('Script Dialog'))

        self.tblScript.setColumnWidth(0, 200)
        self.tblScript.setColumnWidth(1, 50)

        self.gboOptions.setVisible(False)

        # add script folder to sys.path
        sys.path.append(self.getScriptPath())

        self.populateTable()
        self.adjustSize()


    def getScriptPath(self):
        """ Get base path for directory that contains the script files

        Returns:
        String containing absolute base path for script files
        """
        myRoot = os.path.dirname(__file__)
        return os.path.abspath(os.path.join(myRoot, '..', 'script_runner'))

    def populateTable(self):
        """ Populate table list in script dialog with file
        from folder 'script_runner'

        Returns:
        None
        """

        self.tblScript.clearContents()

        # load the list of files in 'script_runner' folder
        myPath = self.getScriptPath()

        # get '.py' files in folder
        myFiles = [
            x for x in os.listdir(myPath) if os.path.splitext(x)[1] == '.py']

        # insert files to table widget
        self.tblScript.setRowCount(len(myFiles))
        for index, filename in enumerate(myFiles):
            self.tblScript.setItem(index, 0, QtGui.QTableWidgetItem(filename))
            self.tblScript.setItem(index, 1, QtGui.QTableWidgetItem(''))


    def runScript(self, theFilename):
        """ runs script in QGIS
        Args:
           * theFilename - the script filename
        Returns:
           not applicable
        Raises:
           no exceptions explicitly raised
        """

        # import script module
        myModule, _ = os.path.splitext(theFilename)
        if sys.modules.has_key(myModule):
            myScript = reload(sys.modules[myModule])
        else:
            myScript = __import__(myModule)

        myCount = int(self.sboCount.value())

        # run script
        for i in range(1, myCount + 1):
            # run in blank project state if checkbox is checked
            if self.cboNewProject.isChecked():
                qgis.utils.iface.newProject()

            # run entry function
            myFunction = myScript.runScript
            if myFunction.func_code.co_argcount == 1:
                myFunction(qgis.utils.iface)
            else:
                myFunction()


    @pyqtSignature('')
    def on_btnRunSelected_clicked(self):
        myCurrentRow = self.tblScript.currentRow()
        myFilename = str(self.tblScript.item(myCurrentRow, 0).text())

        # set status to 'running'
        myStatusItem = self.tblScript.item(myCurrentRow, 1)
        myStatusItem.setText(self.tr('Running'))

        # run script
        try:
            self.runScript(myFilename)
            # set status to 'OK'
            myStatusItem.setText(self.tr('OK'))
        except Exception as ex:
            # set status to 'fail'
            myStatusItem.setText(self.tr('Fail'))

            LOGGER.log(0, ex.message)

            # just reraise the exception
            raise



    @pyqtSignature('')
    def on_btnRefresh_clicked(self):
        self.populateTable()

    @pyqtSignature('bool')
    def on_pbnAdvanced_toggled(self, theFlag):
        if theFlag:
            self.pbnAdvanced.setText(self.tr('Hide advanced options'))
        else:
            self.pbnAdvanced.setText(self.tr('Show advanced options'))

        self.gboOptions.setVisible(theFlag)
        self.adjustSize()
