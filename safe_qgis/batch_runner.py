"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Batch runner dialog.**

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

from StringIO import StringIO
from ConfigParser import ConfigParser, MissingSectionHeaderError

from PyQt4.QtCore import (pyqtSignal, QSettings, QVariant, QString, Qt,
                          QAbstractListModel, QModelIndex, QRect, QSize,
                          QEvent, QUrl)
from PyQt4.QtGui import (QDialog, QFileDialog, QMessageBox, QStyledItemDelegate, QPen, QStyle,
                         QStyleOptionButton, QPainter, QStyleOptionProgressBar, QPushButton,
                         QApplication, QDesktopServices)

from qgis.core import QgsRectangle

from safe_qgis.batch_runner_base import Ui_BatchRunnerBase
from safe_qgis.batch_option import BatchOption

from safe_qgis.map import Map
from safe_qgis.html_renderer import HtmlRenderer
from safe_qgis.exceptions import QgisPathError
from safe_qgis.safe_interface import temp_dir

from safe_qgis import macro
from safe_qgis.utilities import safeTr
from safe_qgis.exceptions import KeywordNotFoundError

LOGGER = logging.getLogger('InaSAFE')


class BatchRunner(QDialog, Ui_BatchRunnerBase):
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

        self.iface = theIface
        myRoot = os.path.dirname(__file__)
        self.defaultSourceDir = os.path.abspath(
            os.path.join(myRoot, '..', 'script_runner'))
        self.sourceDir = self.defaultSourceDir
        self.ignoreBaseDataDir = False

        # initialized task list view
        self.model = TaskModel(self)
        self.itemDelegate = TaskItemDelegate(self)

        self.lvTask.setModel(self.model)
        self.lvTask.setItemDelegate(self.itemDelegate)

        #self.adjustSize()
        self.restoreState()

        self.populate(self.sourceDir)

        # setup signal & slot
        self.pleSourcePath.lePath.textChanged.connect(self.populate)
        self.itemDelegate.runClicked.connect(self.runTask)
        self.itemDelegate.mapClicked.connect(self.openUrl)
        self.itemDelegate.tableClicked.connect(self.openUrl)
        self.itemDelegate.errorDetailClicked.connect(self.showErrorMessage)
        self.pbnRunAll.clicked.connect(self.runAllTask)
        self.pbnOption.clicked.connect(self.showOptionDialog)

    def populate(self, theBasePath):
        self.model.populate(theBasePath, self.sourceDir)

    def restoreState(self):
        """Restore GUI state from configuration file"""

        mySettings = QSettings()

        self.sourceDir = mySettings.value('inasafe/lastSourceDir',
                                          self.defaultSourceDir).toString()
        self.baseDataDir = mySettings.value('inasafe/baseDataDir',
                                            QString('')).toString()
        self.reportDir = mySettings.value('inasafe/reportDir',
                                          self.baseDataDir).toString()
        self.ignoreBaseDataDir = mySettings.value(
            'inasafe/ignoreBaseDataDir',
            self.ignoreBaseDataDir).toBool()

        self.pleSourcePath.setText(self.sourceDir)

    def saveState(self):
        """Save current state of GUI to configuration file"""

        mySettings = QSettings()

        mySettings.setValue('inasafe/lastSourceDir', self.sourceDir)
        mySettings.setValue('inasafe/baseDataDir', self.baseDataDir)
        mySettings.setValue('inasafe/reportDir', self.reportDir)
        mySettings.setValue('inasafe/ignoreBaseDataDir', self.ignoreBaseDataDir)

    def showOptionDialog(self):
        """ Show option dialog """

        myOptions = BatchOption.getOptions(
            self.baseDataDir, self.reportDir, self.ignoreBaseDataDir)

        if myOptions:
            (self.baseDataDir, self.reportDir, self.ignoreBaseDataDir) = \
                myOptions

            self.saveState()

    def runScriptTask(self, theFilename):
        """ Run a python script in QGIS to exercise InaSAFE functionality.

        This functionality was originally intended for verifying that the key
        elements are InaSAFE are loading correctly and available. However,
        the utility of this function is such that you can run any arbitrary
        python scripts with it. As such you can use it it automate
        activities in QGIS, for example automatically running an impact
        assessment in response to an event.

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

        # run as a new project
        self.iface.newProject()

        # run entry function
        myFunction = myScript.runScript
        if myFunction.func_code.co_argcount == 1:
            myFunction(self.iface)
        else:
            myFunction()

    def runScenarioTask(self, theIndex, theTask):
        """Run a simple scenario.
        After scenario has finished, pdf report will be created in
        directory self.reportDir

        Params:
            theTask - a dictionary contains the scenario configuration
        Returns:
            True if success, otherwise return False.
        """

        # always run in new project
        self.iface.newProject()

        myMessage = 'Loading layers: \nRoot: %s\n%s' % (
            theTask['path'], theTask['layers'])
        LOGGER.info(myMessage)

        try:
            macro.addLayers(theTask['path'], theTask['layers'])
        except QgisPathError:
            # set status to 'fail'
            myMessage = 'Loading layers failed: \nRoot: %s\n%s' % (
                theTask['path'], theTask['layers'])
            self.model.setErrorMessage(theIndex, myMessage)
            return False

        # See if we have a preferred impact function
        if 'function' in theTask:
            myFunctionId = theTask['function']
            myResult = macro.setFunctionId(myFunctionId)
            if not myResult:
                myMessage = "cannot set function %s" % theTask['function']
                self.model.setErrorMessage(theIndex, myMessage)
                return False

        # set aggregation layer if exist
        myAggregation = theTask.get('aggregation')
        if myAggregation:
            myResult = macro.setAggregation(myAggregation)
            if not myResult:
                myMessage = "cannot set aggregation %s" % myAggregation
                self.model.setErrorMessage(theIndex, myMessage)
                return False

        # set extent if exist
        myExtent = theTask.get('extent')
        if myExtent:
            # split extent string
            myCoordinate = myExtent.replace(' ', '').split(',')
            myCount = len(myCoordinate)
            if myCount != 4:
                myMessage = 'extent need exactly 4 value but got %s instead' % myCount
                self.model.setErrorMessage(theIndex, myMessage)
                return False

            # parse the value to float type
            try:
                myCoordinate = [float(i) for i in myCoordinate]
            except ValueError as e:
                myMessage = e.message
                self.model.setErrorMessage(theIndex, myMessage)
                return False

            # set the extent according the value
            myExtent = QgsRectangle(*myCoordinate)

            myMessage = 'set layer extent to %s ' % myExtent.asWktCoordinates()
            LOGGER.info(myMessage)

            self.iface.mapCanvas().setExtent(myExtent)

        def onAnalysisDone():
            # NOTE(gigih):
            # Usually after analysis is done, the impact layer
            # become the active layer. <--- WRONG
            myImpactLayer = self.iface.activeLayer()
            myReportDir = str(self.reportDir)
            myMapPath, myTablePath = self.createPDFReport(
                theTask['label'], myReportDir, myImpactLayer)

            # set status to success
            self.model.setReportPath(theIndex, myMapPath, myTablePath)
            self.model.setStatus(theIndex, TaskModel.Success)

        LOGGER.info("Run scenario %s" % theTask['label'])
        macro.runScenario(onAnalysisDone)

        return True

    # @pyqtSignature('')
    # def on_pbnRunAll_clicked(self):
    #     myReport = []
    #     myFailCount = 0
    #     myPassCount = 0
    #
    #     for myRow in range(self.tblScript.rowCount()):
    #         myItem = self.tblScript.item(myRow, 0)
    #         myStatusItem = self.tblScript.item(myRow, 1)
    #
    #         try:
    #             myResult = self.runTask(myItem, myStatusItem)
    #             if myResult:
    #                 # P for passed
    #                 myReport.append('P: %s\n' % str(myItem))
    #                 myPassCount += 1
    #             else:
    #                 myReport.append('F: %s\n' % str(myItem))
    #                 myFailCount += 1
    #         except:
    #             LOGGER.exception('Batch execution failed')
    #             myReport.append('F: %s\n' % str(myItem))
    #             myFailCount += 1
    #
    #     self.showBatchReport(myReport, myPassCount, myFailCount)

    def showBatchReport(self, myReport, myPassCount, myFailCount):
        """Display a report status of Batch Runner"""

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
        myUrl = QUrl('file:///' + myPath)
        QDesktopServices.openUrl(myUrl)

    def runAllTask(self):
        """ Run all batch runner tasks """

        # check existing pdf report and
        # ask user if he want to rewrite existing report
        myPath = str(self.reportDir)
        myTitles = [myTask['label'] for myTask in self.model.tasks]

        myResult = self.checkExistingPDFReport(myPath, myTitles)
        if myResult is False:
            return False

        # run all task without checking existing report
        for myIndex in range(0, len(self.model.tasks)):
            self.runTask(myIndex, False)

        ## TODO: show report


    def runTask(self, theIndex, theCheckExistingReport=True):
        myTask = self.model.tasks[theIndex]

        # set status to running...
        self.model.setStatus(theIndex, TaskModel.Running)

        if myTask['type'] == 'script':
            self.runScriptTask(myTask['source'])
        elif myTask['type'] == 'scenario':
            myPath = str(self.reportDir)
            myTitle = myTask['label']

            # Check existing pdf report.
            # It will prompt user if he want to overwrite the report or not.
            # When user don't want to overwrite the report then
            # the operation must be canceled
            if theCheckExistingReport:
                myResult = self.checkExistingPDFReport(myPath, [myTitle])
                if myResult is False:
                    self.model.setStatus(theIndex, TaskModel.Normal)
                    return False

            myResult = self.runScenarioTask(theIndex, myTask)
            if myResult is False:
                self.model.setStatus(theIndex, TaskModel.Fail)

        else:
            LOGGER.exception('task type not supported: "%s"' % myTask['type'])
            #myResult = False

    def openUrl(self, theIndex, thePath):
        myUrl = QUrl('file:///' + thePath)
        QDesktopServices.openUrl(myUrl)

    def showErrorMessage(self, theIndex, theMessage):
        """ TODO: improve the UI
        """
        QMessageBox.about(self, self.tr("Error Message"), theMessage)

    # def runTask(self, theItem, theStatusItem, theCount=1):
    #     """Run a single task """
    #
    #     # set status to 'running'
    #     theStatusItem.setText(self.tr('Running'))
    #
    #     # .. seealso:: :func:`appendRow` to understand the next 2 lines
    #     myVariant = theItem.data(QtCore.Qt.UserRole)
    #     myValue = myVariant.toPyObject()[0]
    #
    #     myResult = True
    #
    #     if isinstance(myValue, str):
    #         myFilename = myValue
    #         # run script
    #         try:
    #             self.runScriptTask(myFilename, theCount)
    #             # set status to 'OK'
    #             theStatusItem.setText(self.tr('OK'))
    #         except Exception as ex:
    #             # set status to 'fail'
    #             theStatusItem.setText(self.tr('Fail'))
    #
    #             LOGGER.exception('Running macro failed')
    #             myResult = False
    #     elif isinstance(myValue, dict):
    #         myPath = str(self.leBaseDataDir.text())
    #         myTitle = str(theItem.text())
    #
    #         # check existing pdf report
    #         myResult = self.checkExistingPDFReport(myPath, [myTitle])
    #         if myResult is False:
    #             return False
    #
    #         # Its a dict containing files for a scenario
    #         myResult = self.runScenarioTask(myValue)
    #         if not myResult:
    #             theStatusItem.setText(self.tr('Fail'))
    #             myResult = False
    #         else:
    #
    #             # NOTE(gigih):
    #             # Usually after analysis is done, the impact layer
    #             # become the active layer. <--- WRONG
    #             myImpactLayer = self.iface.activeLayer()
    #             self.createPDFReport(myTitle, myPath, myImpactLayer)
    #     else:
    #         LOGGER.exception('data type not supported: "%s"' % myValue)
    #         myResult = False
    #
    #     return myResult

    def getPDFReportPath(self, theBasePath, theTitle):
        """Get PDF report filename based on theBasePath and theTitle.
        Params:
            * theBasePath - base path of pdf report file
            * theTitle - title of report
        Returns:
            a tuple contains the pdf report filename like this
            ('/home/foo/data/title.pdf', '/home/foo/data/title_table.pdf')
        """

        ## parse special variable like {date}
        import datetime
        now = datetime.datetime.now()
        myBasePath = theBasePath.format(date=now.strftime('%Y-%m-%d'))

        myFileName = theTitle.replace(' ', '_')
        myFileName = myFileName + '.pdf'
        myMapPath = os.path.join(myBasePath, myFileName)
        myTablePath = os.path.splitext(myMapPath)[0] + '_table.pdf'

        return (myMapPath, myTablePath)

    def checkExistingPDFReport(self, theBasePath, theTitles):
        """ Check the existence of pdf report in theBasePath.

        Params:
            * theBasePath - base path of pdf report file
            * theTitle - list of report titles
        Returns:
            True if theBasePath contains no reports or User
            agree to overwrite the report, otherwise return False.
        """

        myPaths = []
        for theTitle in theTitles:
            myPDFPaths = self.getPDFReportPath(theBasePath, theTitle)
            myPDFPaths = [x for x in myPDFPaths if os.path.exists(x)]
            myPaths.extend(myPDFPaths)

        # if reports are not founds, just return True
        if len(myPaths) == 0:
            return True

        # setup message box widget
        myMessage = self.tr(
            "PDF Report already exist in %1. Rewrite the files?")
        myMessage = myMessage.arg(theBasePath)

        myDetail = 'Existing PDF Report: \n'
        myDetail = myDetail + '\n'.join(myPaths)

        myMsgBox = QMessageBox(self)
        myMsgBox.setIcon(QMessageBox.Question)
        myMsgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        myMsgBox.setText(myMessage)
        myMsgBox.setDetailedText(myDetail)

        # return the result
        myResult = myMsgBox.exec_()
        return myResult == QMessageBox.Yes

    def createPDFReport(self, theTitle, theBasePath, theImpactLayer):
        """Create PDF report from impact layer.
        Create map & table report PDF based from theImpactLayer data.

        Params:
            * theTitle : the report title.
                         Output filename is based from this variable.
            * theBasePath : output directory
            * theImpactLayer : impact layer instance.
        Returns:
            Tuple of report path with format like this
             (map_path, table_path)

        See also:
            Dock.printMap()
        """

        myMap = Map(self.iface)

        # FIXME: check if theImpactLayer is the real impact layer...
        myMap.setImpactLayer(theImpactLayer)

        LOGGER.debug('Create Report: %s' % theTitle)
        myMapPath, myTablePath = self.getPDFReportPath(theBasePath, theTitle)

        # create map pdf
        myDirPath = os.path.dirname(myMapPath)
        if os.path.exists(myDirPath) is False:
            os.makedirs(myDirPath)

        myMap.printToPdf(myMapPath)

        # create table report pdf
        myHtmlRenderer = HtmlRenderer(myMap.pageDpi)
        myKeywords = myMap.keywordIO.readKeywords(theImpactLayer)
        myHtmlRenderer.printImpactTable(myKeywords, myTablePath)

        myResult = (myMapPath, myTablePath)
        LOGGER.debug("report done %s %s" % myResult)

        return myResult

    def saveCurrentScenario(self):
        """ Save current scenario to text file """
        myTitleDialog = self.tr('Save Scenario')
        myFileName = QFileDialog.getSaveFileName(
            self, myTitleDialog,
            self.sourceDir,
            "Text files (*.txt)"
        )

        # user press 'cancel'
        if not myFileName:
            return

        ### get data layer
        myDock = macro.getDock()

        # get absolute path of exposure & hazard layer
        myExposureLayer = myDock.getExposureLayer()
        myHazardLayer = myDock.getHazardLayer()

        myExposurePath = myExposureLayer.publicSource()
        myHazardPath = myHazardLayer.publicSource()
        myRootPath = os.path.commonprefix([myExposurePath, myHazardPath])

        # get title from keyword, otherwise use filename as title
        try:
            myTitle = myDock.keywordIO.readKeywords(myHazardLayer, 'title')
        except KeywordNotFoundError:
            myTitle = os.path.basename(str(myHazardPath))
            myTitle = os.path.splitext(myTitle)[0]

        myTitle = safeTr(myTitle)
        myFunctionId = myDock.getFunctionID(myDock.cboFunction.currentIndex())

        # simplify the path
        myExposurePath = myExposurePath.split(myRootPath)[1]
        myHazardPath = myHazardPath.split(myRootPath)[1]

        # write to file
        myParser = ConfigParser()
        myParser.add_section(myTitle)
        myParser.set(myTitle, 'path', myRootPath)
        myParser.set(myTitle, 'exposure', myExposurePath)
        myParser.set(myTitle, 'hazard', myHazardPath)
        myParser.set(myTitle, 'function', myFunctionId)

        myParser.write(open(myFileName, 'w'))
        LOGGER.info("save current scenario to %s" % myFileName)


def readScenarios(theFileName):
    """Read keywords dictionary from file

    Args:
        theFilename: Name of file holding scenarios .

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
    myFilename = os.path.abspath(theFileName)

    myBlocks = {}
    myParser = ConfigParser()

    # Parse the file content.
    # if the content don't have section header
    # we use the filename.
    try:
        myParser.read(myFilename)
    except MissingSectionHeaderError:
        myBaseName = os.path.basename(theFileName)
        myName = os.path.splitext(myBaseName)[0]
        mySection = '[%s]\n' % myName
        myContent = mySection + open(myFilename).read()
        myParser.readfp(StringIO(myContent))

    # convert to dictionary
    for mySection in myParser.sections():
        myItems = myParser.items(mySection)
        myBlocks[mySection] = {}
        for myKey, myValue in myItems:
            myBlocks[mySection][myKey] = myValue

    # Ok we have generated a structure that looks like this:
    # myBlocks = {{ 'foo' : { 'a': 'b', 'c': 'd'},
    #           { 'bar' : { 'd': 'e', 'f': 'g'}}
    # where foo and bar are scenarios and their dicts are the options for
    # that scenario (e.g. hazard, exposure etc)
    return myBlocks


class TaskModel(QAbstractListModel):
    """Task Model is class that contains all batch runner tasks.

    Each task have format like this:

    Scenario
    {
        'type': 'scenario',
        'label': 'scenario name,
        'path': None or '/absolute/path/for/data',
        'hazard': 'relative/hazard/path',
        'exposure': 'relative/exposure/path',
        'function': 'function id',
        'aggregation': None or '/absolute/path/for/data',
        'layers': list of all layer path
    }

    Script
    {
        'type': 'script',
       'label': 'script name',
       'source': '/absolute/path/to/script.py'
    }

    """

    # Enum for status of task
    Normal = 0
    Running = 1
    Fail = 3
    Success = 4

    def __init__(self, theParent=None):
        """ Initialize TaskModel.
        Params:
            * theParent - parent widget
        """

        QAbstractListModel.__init__(self, theParent)

        self.tasks = []
        self.currentRunningTask = None

    def rowCount(self, theParent=QModelIndex()):
        """ Get the task count """
        return len(self.tasks)

    def data(self, theIndex, theRole):
        """ Get data of task.
        Params:
            * theIndex : QModelIndex - index of item in model
            * theRole - the role of data
        Returns:
            the label of task if theRole is Qt.DisplayRole, otherwise
            return a dictionary of task data.
        """
        myData = self.tasks[theIndex.row()]

        if theIndex.isValid() and theRole == Qt.DisplayRole:
            return QVariant(myData['label'])
        else:
            # see for details of why we follow this pattern
            # http://stackoverflow.com/questions/9257422/
            # how-to-get-the-original-python-data-from-qvariant
            # Make the value immutable.
            myVariant = QVariant((myData,))

            return myVariant

    def setStatus(self, theIndex, theFlag):
        """ Set status of task
        Params:
            * theIndex - index of task in Model
            * theFlag - status value of task:
                        TaskModel.Normal, TaskModel.Running,
                        TaksModel.Fail, or TaskModel.Success
        """

        if self.tasks[theIndex].get('status') == TaskModel.Running:
            self.currentRunningTask = None

        # make sure that only zero or one task is running...
        if theFlag == TaskModel.Running:
            if self.currentRunningTask is not None:
                self.setStatus(self.currentRunningTask, TaskModel.Normal)
            else:
                self.currentRunningTask = theIndex

        # set status
        self.tasks[theIndex]['status'] = theFlag

        myModelIndex = self.index(theIndex, 0)
        self.dataChanged.emit(myModelIndex, myModelIndex)

    def setReportPath(self, theIndex, theMapPath, theTablePath):
        self.tasks[theIndex]['map_path'] = theMapPath
        self.tasks[theIndex]['table_path'] = theTablePath

    def setErrorMessage(self, theIndex, theMessage):
        self.tasks[theIndex]['message'] = theMessage

    def populate(self, theSourcePath, theDataPath):
        """ Populate model with files from theSourcePath directory.

        Args:
            theSourcePath : QString - path where .txt & .py reside
            theDataPath : QString - default data layer directory for scenario file to search
        """

        self.tasks = []

        myPath = str(theSourcePath)
        myDataPath = str(theDataPath)

        # only support .py and .txt files
        for myFile in os.listdir(myPath):
            myExt = os.path.splitext(myFile)[1]
            myAbsPath = os.path.join(myPath, myFile)

            if myExt == '.py':
                self.tasks.append({
                    'type': 'script',
                    'label': myFile,
                    'source': os.path.join(myAbsPath, myFile)
                })

            elif myExt == '.txt':
                # insert scenarios from file into table widget
                for myKey, myValue in readScenarios(myAbsPath).iteritems():

                    myLayers = []

                    ## NOTE: hazard & exposure is must!!
                    if 'hazard' in myValue:
                        myLayers.append(myValue['hazard'])
                    if 'exposure' in myValue:
                        myLayers.append(myValue['exposure'])

                    # optional
                    if 'aggregation' in myValue:
                        myLayers.append(myValue['aggregation'])

                    self.tasks.append({
                        'type': 'scenario',
                        'label': myKey,
                        'path': myValue.get('path') or myDataPath,
                        'hazard': myValue['hazard'],
                        'exposure': myValue['exposure'],
                        'function': myValue['function'],
                        'aggregation': myValue.get('aggregation'),
                        'extent': myValue.get('extent'),
                        'layers': myLayers
                    })


class TaskItemDelegate(QStyledItemDelegate):
    """ TaskItemDelegate is class that have role to
    render single task data to screen.

    NOTE(Gigih):
    This class is too complicated.....
    QStyledItemDelegate don't allow inserting widget so
    we must draw the widget ourselves in paint() and handle
    the event in editorEvent().

    Must find other approach that allow us to draw complex widget
    but flexible enough to split data related function in TaskModel.

    """

    runClicked = pyqtSignal(int)
    mapClicked = pyqtSignal(int, str)
    tableClicked = pyqtSignal(int, str)
    errorDetailClicked = pyqtSignal(int, str)

    def __init__(self, theParent=None, *theArgs):
        QStyledItemDelegate.__init__(self, theParent, *theArgs)

        self.runButtonStyle = QStyleOptionButton()
        self.runButtonStyle.text = self.tr("Run")
        self.runButtonStyle.state = QStyle.State_Enabled

        self.margin = 10
        self.progressBarSize = QSize(140, 24)
        self.runButtonSize = QSize(100, 24)
        self.labelSize = QSize(100, 24)

        self.isRunButtonPressed = False

    def getRunButtonRect(self, theOption):
        myRect = QRect(theOption.rect)
        myRect.setY(theOption.rect.y() + self.margin)
        myRect.setX(
            theOption.rect.right() - self.runButtonSize.width() - self.margin)
        myRect.setSize(self.runButtonSize)

        return myRect

    def getProgressBarRect(self, theOption):
        myRect = QRect(theOption.rect)
        myRect.setY(theOption.rect.y() + self.margin)
        myRect.setX(theOption.rect.right() -
                    self.progressBarSize.width() - self.margin)
        myRect.setSize(self.progressBarSize)

        return myRect

    def getMapLabelRect(self, theOption):
        myRect = QRect(theOption.rect)
        myRect.setY(theOption.rect.y() + self.margin + 30)
        myRect.setX(theOption.rect.x() + self.margin + 70)
        myRect.setSize(self.labelSize)

        return myRect

    def getTableLabelRect(self, theOption):
        myRect = QRect(theOption.rect)
        myRect.setY(theOption.rect.y() + self.margin + 30)
        myRect.setX(theOption.rect.x() + self.margin + 250)
        myRect.setSize(self.labelSize)

        return myRect

    def getDetailLabelRect(self, theOption):
        myRect = QRect(theOption.rect)
        myRect.setY(theOption.rect.y() + self.margin + 30)
        myRect.setX(theOption.rect.x() + self.margin + 200)
        myRect.setSize(self.labelSize)

        return myRect

    def sizeHint(self, theOption, theIndex=None):
        myVariant = theIndex.data(Qt.UserRole)
        myTask = myVariant.toPyObject()[0]
        myStatus = myTask.get('status')
        if myStatus == TaskModel.Success or myStatus == TaskModel.Fail:
            return QSize(450, 80)
        else:
            return QSize(450, 40)

    def paint(self, thePainter, theOption, theIndex):

        myAppStyle = QApplication.style()
        thePainter.save()

        thePainter.setRenderHint(QPainter.Antialiasing, True)

        # .. seealso:: :func:`TaskModel.data` to understand the next 2 lines
        myVariant = theIndex.data(Qt.UserRole)
        myTask = myVariant.toPyObject()[0]
        myStatus = myTask.get('status')

        # draw icon

        # draw label text
        myLabel = myTask.get('label')
        myLabelRect = QRect(theOption.rect)
        myLabelRect.setY(theOption.rect.y() + self.margin)
        myLabelRect.setX(theOption.rect.x() + self.margin)

        thePainter.setPen(QPen(Qt.black))
        thePainter.drawText(myLabelRect, Qt.AlignLeft, myLabel)

        # draw run button
        if myStatus is None or myStatus == TaskModel.Normal:
            myButton = QStyleOptionButton(self.runButtonStyle)
            myButton.rect = self.getRunButtonRect(theOption)

            if self.isRunButtonPressed:
                myButton.state = QStyle.State_Sunken

            myAppStyle.drawControl(QStyle.CE_PushButton, myButton, thePainter)
        # draw progress bar
        elif myStatus == TaskModel.Running:
            myProgressBar = QStyleOptionProgressBar()
            myProgressBar.text = self.tr("Running...")
            myProgressBar.progress = 4
            myProgressBar.maximum = 5
            myProgressBar.rect = self.getProgressBarRect(theOption)

            #myAppStyle.drawControl(QStyle.CE_ProgressBarGroove, myProgressBar, thePainter)
            myAppStyle.drawControl(QStyle.CE_ProgressBar, myProgressBar, thePainter)
            #myAppStyle.drawControl(QStyle.CE_ProgressBarContents, myProgressBar, thePainter)
            #myAppStyle.drawControl(QStyle.CE_ProgressBarLabel, myProgressBar, thePainter)

        elif myStatus == TaskModel.Fail:
            # text: Fail
            myLabel = self.tr("Scenario failed. Click here for ")
            myLabelRect = QRect(theOption.rect)
            myLabelRect.setY(theOption.rect.y() + self.margin + 30)
            myLabelRect.setX(theOption.rect.x() + self.margin)

            thePainter.setPen(QPen(Qt.black))
            thePainter.drawText(myLabelRect, Qt.AlignLeft, myLabel)
            # text: detail
            myLabel = self.tr("detail")
            myLabelRect = self.getDetailLabelRect(theOption)

            thePainter.setPen(QPen(Qt.blue))
            thePainter.drawText(myLabelRect, Qt.AlignLeft, myLabel)

        elif myStatus == TaskModel.Success:
            if myTask['type'] == 'script':
                # text: success
                myLabel = self.tr("Success")
                myLabelRect = QRect(theOption.rect)
                myLabelRect.setY(theOption.rect.y() + self.margin + 30)
                myLabelRect.setX(theOption.rect.x() + self.margin)
            else:
                # text: report
                myLabel = self.tr("Report")
                myLabelRect = QRect(theOption.rect)
                myLabelRect.setY(theOption.rect.y() + self.margin + 30)
                myLabelRect.setX(theOption.rect.x() + self.margin)

                thePainter.setPen(QPen(Qt.black))
                thePainter.drawText(myLabelRect, Qt.AlignLeft, myLabel)

                thePainter.setPen(QPen(Qt.blue))

                ## text: map path
                myLabel = os.path.basename(myTask.get('map_path'))
                myLabelRect = self.getMapLabelRect(theOption)
                thePainter.drawText(myLabelRect, Qt.AlignLeft, myLabel)

                ## text: table path
                myLabel = os.path.basename(myTask.get('table_path'))
                myLabelRect = self.getTableLabelRect(theOption)
                thePainter.drawText(myLabelRect, Qt.AlignLeft, myLabel)

        thePainter.restore()

    def editorEvent(self, theEvent, theItemModel, theOption, theModelIndex):
        """
        :param theEvent:QEvent
        :param theItemModel:
        :param theStyle:
        :param theModelIndex:
        :return:
        """

        # .. seealso:: :func:`appendRow` to understand the next 2 lines
        myVariant = theModelIndex.data(Qt.UserRole)
        myTask = myVariant.toPyObject()[0]
        myStatus = myTask.get('status')

        ## listen event for run button
        if myStatus is None or myStatus == TaskModel.Normal:
            myRunButtonRect = self.getRunButtonRect(theOption)
            myType = theEvent.type()
            if myType == QEvent.MouseButtonRelease:
                if myRunButtonRect.contains(theEvent.pos()):
                    self.isRunButtonPressed = False
                    self.runClicked.emit(theModelIndex.row())
            elif myType == QEvent.MouseButtonPress:
                if myRunButtonRect.contains(theEvent.pos()):
                    self.isRunButtonPressed = True
        ## list event for report path
        elif myStatus == TaskModel.Success:
            myMapRect = self.getMapLabelRect(theOption)
            myTableRect = self.getTableLabelRect(theOption)
            myType = theEvent.type()
            myPos = theEvent.pos()
            if myType == QEvent.MouseButtonRelease:
                if myMapRect.contains(myPos):
                    self.mapClicked.emit(theModelIndex.row(), myTask['map_path'])
                elif myTableRect.contains(myPos):
                    self.tableClicked.emit(theModelIndex.row(), myTask['table_path'])
            elif myType == QEvent.MouseButtonPress:
                pass
        elif myStatus == TaskModel.Fail:
            myDetailRect = self.getDetailLabelRect(theOption)
            myType = theEvent.type()
            myPos = theEvent.pos()
            if myType == QEvent.MouseButtonRelease:
                if myDetailRect.contains(myPos):
                    self.errorDetailClicked.emit(theModelIndex.row(), myTask['message'])
            elif myType == QEvent.MouseButtonPress:
                pass

        return False

if __name__ == '__main__':
    from PyQt4.QtGui import QApplication
    from PyQt4.QtCore import QCoreApplication
    import sys

    QCoreApplication.setOrganizationDomain('aifdr')
    QCoreApplication.setApplicationName('inasafe')

    app = QApplication(sys.argv)
    a = BatchRunner()

    # experiment
    model = a.model

    def dummyRunScenarioTask(theIndex, theTask):
        print "dummy function"
        model.setReportPath(theIndex,
                            r'C:\Users\bungcip\Desktop\Bangunan_terendam.pdf',
                            r'C:\Users\bungcip\Desktop\Bangunan_terendam.pdf')
        model.setStatus(theIndex, TaskModel.Success)

    a.runScenarioTask = dummyRunScenarioTask

    #a.model.setStatus(0, TaskModel.Running)
#    a.model.setReportPath(1, r'C:\Users\bungcip\Desktop\Bangunan_terendam.pdf',
 #                         r'C:\Users\bungcip\Desktop\Bangunan_terendam.pdf')
#    a.model.setStatus(1, TaskModel.Success)

    # a.model.setErrorMessage(2, "Error lha")
    # a.model.setStatus(2, TaskModel.Fail)

    a.show()

    #a.saveCurrentScenario()

    app.exec_()

