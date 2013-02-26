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
from PyQt4.QtCore import (pyqtSignature, QSettings, QVariant, QString, Qt)
from PyQt4.QtGui import (QDialog, QFileDialog, QTableWidgetItem)

from script_dialog_base import Ui_ScriptDialogBase

from safe_qgis.map import Map
from safe_qgis.html_renderer import HtmlRenderer
from safe_qgis.exceptions import QgisPathError
from safe_qgis.safe_interface import temp_dir

from safe_qgis import macro

LOGGER = logging.getLogger('InaSAFE')


class ScriptDialog(QDialog, Ui_ScriptDialogBase):
    """Script Dialog for InaSAFE."""

    def __init__(self, theParent=None, theIface=None):
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
        self.setWindowTitle(self.tr('Script Dialog'))
        LOGGER.info('Script runner dialog started')

        self.iface = theIface
        self.basePath = getScriptPath()

        myHeaderView = self.tblScript.horizontalHeader()
        myHeaderView.setResizeMode(0, QtGui.QHeaderView.Stretch)
        myHeaderView.setResizeMode(1, QtGui.QHeaderView.Interactive)

        self.tblScript.setColumnWidth(0, 200)
        self.tblScript.setColumnWidth(1, 50)

        self.gboOptions.setVisible(False)

        # Add script folder to sys.path.
        sys.path.append(self.basePath)

        self.populateTable(self.basePath)
        self.adjustSize()

        # get the base data path from settings if available
        mySettings = QtCore.QSettings()
        myPath = mySettings.value('inasafe/baseDataDir', QtCore.QString(''))
        self.leBaseDataDir.setText(myPath.toString())

    @pyqtSignature('QString')
    def on_leBaseDataDir_changed(self, theString):
        """Handler for when user changes data base path.
        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        mySettings = QSettings()
        mySettings.setValue('inasafe/baseDataDir',
                            theString)

    @pyqtSignature('')  # prevents actions being handled twice
    def on_tbBaseDataDir_clicked(self):
        """Autoconnect slot activated when the select cache file tool button is
        clicked,
        Args:
            None
        Returns:
            None
        Raises:
            None
        """
        mySettings = QSettings()
        myPath = mySettings.value(
            'inasafe/baseDataDir', QString('')).toString()
        myNewPath = QFileDialog.getExistingDirectory(
            self,
            self.tr('Set the base directory for data packages'),
            myPath,
            QFileDialog.ShowDirsOnly)
        self.leBaseDataDir.setText(myNewPath)
        mySettings.setValue('inasafe/baseDataDir', myNewPath)

    def populateTable(self, theBasePath):
        """ Populate table with files from theBasePath directory.

        Args:
            None

        Returns:
            None

        Raises:
            None
        """

        self.tblScript.clearContents()

        # only support .py and .txt files
        for myFile in os.listdir(theBasePath):
            myExt = os.path.splitext(myFile)[1]
            myAbsPath = os.path.join(theBasePath, myFile)

            if myExt == '.py':
                appendRow(self.tblScript, myFile, myAbsPath)
            elif myExt == '.txt':
                LOGGER.info('looking for scenarios in %s' % myAbsPath)
                # insert scenarios from file into table widget
                for myKey, myValue in readScenarios(myAbsPath).iteritems():
                    LOGGER.info('Found scenario: %s:%s in %s' % (
                        myKey, myValue, myAbsPath
                    ))
                    appendRow(self.tblScript, myKey, myValue)

    def runScript(self, theFilename, theCount=1):
        """ Run a python script in QGIS to exercise InaSAFE functionality.

        This functionality was originally intended for verifying that the key
        elements are InaSAFE are loading correctly and available. However,
        the utility of this function is such that you can run any arbitrary
        python scripts with it. As such you can use it it automate
        activities in QGIS, for example automatically running an impact
        assessment in response to an event.

        .. note:: This is a note.

        .. warning:: This is a warning.

        Args:
           * theFilename: str - the script filename.
           * theCount: int - the number of times the script must be run.

        Returns:
           not applicable

        Raises:
           no exceptions explicitly raised
        """

        # import script module
        myModule, _ = os.path.splitext(theFilename)
        if myModule in sys.modules:
            myScript = reload(sys.modules[myModule])
        else:
            myScript = __import__(myModule)

        # run script
        for i in range(1, theCount + 1):
            # run as a new project
            self.iface.newProject()

            # run entry function
            myFunction = myScript.runScript
            if myFunction.func_code.co_argcount == 1:
                myFunction(self.iface)
            else:
                myFunction()

    def runTextFile(self, theItem):
        """ FIXME:(gigih) change function name """
        myRoot = str(self.leBaseDataDir.text())

        myPaths = []
        if 'hazard' in theItem:
            myPaths.append(theItem['hazard'])
        if 'exposure' in theItem:
            myPaths.append(theItem['exposure'])
        if 'aggregation' in theItem:
            myPaths.append(theItem['aggregation'])

        # always run in new project
        self.iface.newProject()

        LOGGER.info('Loading layers: \nRoot: %s\n%s' % (
                    myRoot, myPaths))
        try:
            macro.addLayers(myRoot, myPaths)
        except QgisPathError:
            # set status to 'fail'
            LOGGER.exception('Loading layers failed: \nRoot: %s\n%s' % (
                myRoot, myPaths))
            return False

        # See if we have a preferred impact function
        if 'function' in theItem:
            myFunctionId = theItem['function']
            myResult = macro.setFunctionId(myFunctionId)
            if not myResult:
                return False

        if 'aggregation' in theItem:
            myResult = macro.setAggregationLayer(theItem['aggregation'])
            if not myResult:
                return False

        return True

    @pyqtSignature('')
    def on_pbnRunAll_clicked(self):
        myReport = []
        myFailCount = 0
        myPassCount = 0
        for myRow in range(self.tblScript.rowCount()):
            myItem = self.tblScript.item(myRow, 0)
            myStatusItem = self.tblScript.item(myRow, 1)

            try:
                myResult = self.runTask(myItem, myStatusItem)
                if myResult:
                    # P for passed
                    myReport.append('P: %s\n' % str(myItem))
                    myPassCount += 1
                else:
                    myReport.append('F: %s\n' % str(myItem))
                    myFailCount += 1
            except:
                LOGGER.exception('Batch execution failed')
                myReport.append('F: %s\n' % str(myItem))
                myFailCount += 1

        myPath = os.path.join(temp_dir(), 'batch-report.txt')
        myReportFile = file(myPath, 'wt')
        myReportFile.write(' InaSAFE Batch Report File\n')
        myReportFile.write('-----------------------------\n')
        for myLine in myReport:
            myReportFile.write(myLine)
        myReportFile.write('-----------------------------\n')
        myReportFile.write('Total passed: %s\n' % myPassCount)
        myReportFile.write('Total failed: %s\n' % myFailCount)
        myReportFile.write('Total tasks: %s\n' % len(myReport))
        myReportFile.write('-----------------------------\n')
        myReportFile.close()
        LOGGER.info('Log written to %s' % myPath)
        myUrl = QtCore.QUrl('file:///' + myPath)
        QtGui.QDesktopServices.openUrl(myUrl)

    def runTask(self, theItem, theStatusItem):
        """ run task """

        # set status to 'running'
        theStatusItem.setText(self.tr('Running'))

        # .. seealso:: :func:`appendRow` to understand the next 2 lines
        myVariant = theItem.data(QtCore.Qt.UserRole)
        myValue = myVariant.toPyObject()[0]

        myResult = True

        if isinstance(myValue, str):
            myFilename = myValue
            # run script
            try:
                self.runScript(myFilename, self.sboCount.value())
                # set status to 'OK'
                theStatusItem.setText(self.tr('OK'))
            except Exception as ex:
                # set status to 'fail'
                theStatusItem.setText(self.tr('Fail'))

                LOGGER.exception('Running macro failed')
                myResult = False
        elif isinstance(myValue, dict):
            # Its a dict containing files for a scenario
            myResult = self.runTextFile(myValue)
            if not myResult:
                theStatusItem.setText(self.tr('Fail'))
                myResult = False
        else:
            LOGGER.exception('data type not supported: "%s"' % myValue)
            myResult = False

        ## save pdf
        ##FIXME: not working....
        if myResult:
            myPath = str(self.leBaseDataDir.text())
            myTitle = str(theItem.text())
            self.createReport(myTitle, myPath)

        return myResult

    def createReport(self, theTitle, theBasePath):
        """Create PDF report.
        initial implementation of pdf report.

        See also:
            dock.printMap
        """
        myMap = Map(self.iface)
        myMap.setImpactLayer(self.iface.activeLayer())

        LOGGER.debug('Create Report: %s' % theTitle)

        myFileName = theTitle + '.pdf'
        myFileName = myFileName.replace(' ', '_')
        myMapPdfFilePath = os.path.join(theBasePath, myFileName)

        myTableFilename = os.path.splitext(myMapPdfFilePath)[0] + '_table.pdf'
        myHtmlRenderer = HtmlRenderer(thePageDpi=myMap.pageDpi)
        myKeywords = myMap.keywordIO.readKeywords(self.iface.activeLayer())
        myHtmlRenderer.printImpactTable(
            myKeywords, theFilename=myTableFilename)

        myMap.printToPdf(myMapPdfFilePath)

        LOGGER.debug('Report: %s Done' % theTitle)


    @pyqtSignature('')
    def on_btnRunSelected_clicked(self):
        """Run the selected item. """
        myCurrentRow = self.tblScript.currentRow()
        myItem = self.tblScript.item(myCurrentRow, 0)
        myStatusItem = self.tblScript.item(myCurrentRow, 1)

        self.runTask(myItem, myStatusItem)

    @pyqtSignature('')
    def on_btnRefresh_clicked(self):
        self.populateTable(self.basePath)

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
        theFilename: Name of file holding scenarios - should be placed
            in the script_runner directory.

    Returns:
        Dictionary of with structure like this
        {{ 'foo' : { 'a': 'b', 'c': 'd'},
            { 'bar' : { 'd': 'e', 'f': 'g'}}

    Raises: None

    A scenarios file may look like this:

        [jakarta_flood]
        hazard: /path/to/hazard.tif
        exposure: /path/to/exposure.tif
        function: function_id
        aggregation: /path/to/aggregation_layer.tif
        extent: minx, miny, maxx, maxy
    """

    # Input checks
    myFilename = os.path.abspath(theFilename)
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
        # Remove trailing (but not preceding!) whitespace
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
    # I think we can delete this? TS
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

    Args:
        None

    Returns:
        str: String containing absolute base path for script files

    Raises:
        None
    """
    myRoot = os.path.dirname(__file__)
    return os.path.abspath(os.path.join(myRoot, '..', 'script_runner'))


def appendRow(theTable, theLabel, theData):
    """ Append new row to table widget.
     Args:
        * theTable - a QTable instance
        * theLabel - label for the row.
        * theData  - custom data associated with theLabel value.
     Returns:
        None
     Raises:
        None
    """
    myRow = theTable.rowCount()
    theTable.insertRow(theTable.rowCount())

    myItem = QTableWidgetItem(theLabel)

    # see for details of why we follow this pattern
    # http://stackoverflow.com/questions/9257422/
    # how-to-get-the-original-python-data-from-qvariant
    # Make the value immutable.
    myVariant = QVariant((theData,))
    # To retrieve it again you would need to do:
    #myValue = myVariant.toPyObject()[0]
    myItem.setData(Qt.UserRole, myVariant)

    theTable.setItem(myRow, 0, myItem)
    theTable.setItem(myRow, 1, QTableWidgetItem(''))


if __name__ == '__main__':
    from PyQt4.QtGui import QApplication
    import sys

    app = QApplication(sys.argv)
    a = ScriptDialog()
    a.show()
    app.exec_()

