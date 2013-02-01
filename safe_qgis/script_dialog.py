"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Script runner dialog.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'bungcip@gmail.com & tim@linfiniti.com'
__revision__ = '$Format:%H$'
__date__ = '01/10/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import sys
import logging
import re

from PyQt4 import QtGui, QtCore
from PyQt4.QtCore import pyqtSignature

import qgis

from script_dialog_base import Ui_ScriptDialogBase

from safe_qgis import macro

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
        LOGGER.info('Script runner dialog started')

        myHeaderView = self.tblScript.horizontalHeader()
        myHeaderView.setResizeMode(0, QtGui.QHeaderView.Stretch);
        myHeaderView.setResizeMode(1, QtGui.QHeaderView.Interactive);

        self.tblScript.setColumnWidth(0, 200)
        self.tblScript.setColumnWidth(1, 50)

        self.gboOptions.setVisible(False)

        # Add script folder to sys.path.
        sys.path.append(getScriptPath())

        self.populateTable()
        self.adjustSize()

    def populateTable(self):
        """ Populate table with files from folder 'script_runner' directory.

        Args:
            None

        Returns:
            None
        """

        self.tblScript.clearContents()

        # load the list of files in 'script_runner' folder
        myPath = getScriptPath()

        # get '.py' files in folder
        myFiles = [
            x for x in os.listdir(myPath) if os.path.splitext(x)[1] == '.py']

        # insert files to table widget
        self.tblScript.setRowCount(len(myFiles))
        for myIndex, myFilename in enumerate(myFiles):
            self.tblScript.setItem(
                myIndex, 0, QtGui.QTableWidgetItem(myFilename))
            self.tblScript.setItem(
                myIndex, 1, QtGui.QTableWidgetItem(''))

        # get '.txt' files in folder
        myFiles = [
            x for x in os.listdir(myPath) if os.path.splitext(x)[1] == '.txt']

        for myFile in myFiles:
            LOGGER.info('looking for scenarios in %s' % myFile)
            # insert scenarios from file into table widget
            for myKey, myValue in readScenarios('test.txt').iteritems():
                LOGGER.info('Found scenario: %s:%s in %s' % (
                    myKey, myValue, myFile
                ))
                self.tblScript.insertRow(self.tblScript.rowCount())
                myRow = self.tblScript.rowCount() - 1
                myItem = QtGui.QTableWidgetItem(myKey)
                # see for details of why we follow this pattern
                # http://stackoverflow.com/questions/9257422/
                # how-to-get-the-original-python-data-from-qvariant
                # Make the value immutable.
                myVariant = QtCore.QVariant((myValue,))
                # To retrieve it again you would need to do:
                #myValue = myVariant.toPyObject()[0]
                myItem.setData(QtCore.Qt.UserRole, myVariant)
                self.tblScript.setItem(myRow, 0, myItem)
                self.tblScript.setItem(myRow, 1, QtGui.QTableWidgetItem(''))

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
    def on_pbnRunAll_clicked(self):
        for myRow in range(self.tblScript.rowCount()):
            self.tblScript.selectRow(myRow)
            try:
                self.on_btnRunSelected_clicked()
            except:
                LOGGER.exception('Batch execution failed')

    @pyqtSignature('')
    def on_btnRunSelected_clicked(self):
        myCurrentRow = self.tblScript.currentRow()
        # See if this is a python script or a scenario read from a text file
        myItem = self.tblScript.item(myCurrentRow, 0)
        if myItem.data(QtCore.Qt.UserRole).isNull():
            # Its a python script
            myFilename = myItem.text()

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

                LOGGER.exception('Running macro failed')

                # just re raise the exception
                raise
        else:
            # Its a dict containing files for a scenario
            #myText = myItem.text()
            # .. seealso:: :func:`populateTable` to understand the next 2 lines
            myVariant = myItem.data(QtCore.Qt.UserRole)
            myValue = myVariant.toPyObject()[0]
            # Set status to 'running'
            myStatusItem = self.tblScript.item(myCurrentRow, 1)
            myStatusItem.setText(self.tr('Running'))

            myRoot = os.path.abspath(os.path.join(
                os.path.realpath(os.path.dirname(__file__)),
                                          '..',
                                          '..',
                                          'inasafe_data'))
            myPaths = []
            if 'hazard' in myValue:
                myPaths.append(myValue['hazard'])
            if 'exposure' in myValue:
                myPaths.append(myValue['exposure'])
            if 'aggregation' in myValue:
                myPaths.append(myValue['aggregation'])
            if self.cboNewProject.isChecked():
                qgis.utils.iface.newProject()
            # TODO support specific impact function
            macro.addLayers(myRoot, myPaths)


            # Run script
            try:
                LOGGER.info('Running scenario: %s' % myValue)
                macro.runScenario()
                # set status to 'OK'
                myStatusItem.setText(self.tr('OK'))
            except Exception as ex:
                # set status to 'fail'
                myStatusItem.setText(self.tr('Fail'))
                LOGGER.exception('Running macro failed')
                # just re raise the exception
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


def readScenarios(theFilename):
    """Read keywords dictionary from file

    Args:
        * theFilename: Name of file holding scenarios - should be placed
            in the script_runner directory.

    Returns:
        None

    Raises: None

    A scenarios file may look like this:

        [jakarta_flood]
        hazard: /path/to/hazard.tif
        exposure: /path/to/exposure.tif
        function: function_id
        aggregation: /path/to/aggregation_layer.tif
    """

    # Input checks
    myFilename = os.path.join(getScriptPath(), theFilename)
    myBasename, myExtension = os.path.splitext(theFilename)

    myMessage = ('Unknown extension for file %s. '
                 'Expected %s.txt' % (myFilename, myBasename))
    if '.txt' != myExtension:
        LOGGER.error(myMessage)
        return

    if not os.path.isfile(myFilename):
        return {}

    # Read all entries
    myBlocks = {}
    myKeys = {}
    myFile = open(myFilename, 'r')
    myBlock = None
    myFirstKeys = None
    for line in myFile.readlines():
        # Remove trailing (but not preceeding!) whitespace
        # FIXME: Can be removed altogether
        myLine = line.rstrip()

        # Ignore blank lines
        if myLine == '':
            continue

        # Check if it is an ini style group header
        myBlockFlag = re.search(r'^\[.*]$', myLine, re.M | re.I)

        if myBlockFlag:
            # Write the old block if it exists - must have a current
            # block to prevent orphans
            if len(myKeys) > 0 and myBlock is not None:
                myBlocks[myBlock] = myKeys
            if myFirstKeys is None and len(myKeys) > 0:
                myFirstKeys = myKeys
                # Now set up for a new block
            myBlock = myLine[1:-1]
            # Reset the keys each time we encounter a new block
            # until we know we are on the desired one
            myKeys = {}
            continue

        if ':' not in myLine:
            continue
        else:
            # Get splitting point
            myIndex = myLine.find(':')

            # Take key as everything up to the first ':'
            myKey = myLine[:myIndex]

            # Take value as everything after the first ':'
            myValue = myLine[myIndex + 1:].strip()

        # Add entry to dictionary
        myKeys[myKey] = myValue

    myFile.close()

    # Write out any unfinalised block data
    if len(myKeys) > 0 and myBlock is not None:
        myBlocks[myBlock] = myKeys
    if myFirstKeys is None:
        myFirstKeys = myKeys

    # Ok we have generated a structure that looks like this:
    # myBlocks = {{ 'foo' : { 'a': 'b', 'c': 'd'},
    #           { 'bar' : { 'd': 'e', 'f': 'g'}}
    # where foo and bar are scenarios and their dicts are the options for
    # that scenario (e.g. hazard, exposure etc)
    return myBlocks

def getScriptPath():
    """ Get base path for directory that contains the script files

    Returns:
    String containing absolute base path for script files
    """
    myRoot = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(myRoot, '..', 'script_runner'))
