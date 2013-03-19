"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Script runner test cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com & bungcip@gmail.com'
__date__ = '1/02/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import unittest
import logging

# Needed though not used below
from PyQt4.QtCore import Qt
from PyQt4.QtGui import QApplication, QTableWidget  # pylint: disable=W0611
from safe_qgis.utilities_test import getQgisTestApp, unitTestDataPath
from safe_qgis.batch_runner import (BatchRunner, readScenarios, appendRow)

QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()
LOGGER = logging.getLogger('InaSAFE')
CONTROL_INPUT_DIR = os.path.join(os.path.dirname(__file__),
                                 'test_data/test_files')

LOGGER = logging.getLogger('InaSAFE')


class ScriptDialogTest(unittest.TestCase):

    #def setUp(self):
    #    self.scriptDialog = ScriptDialog(PARENT, IFACE)

    def test_readScenarios1(self):
        """Test if we can load scenarios from a multi section file text."""
        myFile = os.path.join(CONTROL_INPUT_DIR, "test-scenario-input.txt")
        myDictionary = readScenarios(myFile)

        myExpectedDictionary = {
            'Merapi_volcano_osm_buildings': {
                'exposure': 'Merapi/Data/bangunan.shp',
                'hazard': 'Merapi/Data/merapi_krb.shp',
                'function': 'Volcano Building Impact',
                'extent': '110.13,-7.81,110.67,-7.50'
            },
            'Merapi_volcano_population': {
                'exposure': 'Merapi/Data/jawa2_popmap10_all.tif',
                'hazard': 'Merapi/Data/merapi_krb.shp',
                'function': 'Volcano Polygon Hazard Population',
                'extent': '110.13,-7.81,110.67,-7.50'
            },
        }
        self.assertDictEqual(myExpectedDictionary, myDictionary)

    def test_readScenarios2(self):
        """Test if we can load scenarios from a single section file text."""
        myFile = os.path.join(CONTROL_INPUT_DIR, "test-scenario-input2.txt")
        myDictionary = readScenarios(myFile)

        myExpectedDictionary = {
            'test-scenario-input2': {
                'exposure': 'Merapi/Data/bangunan.shp',
                'hazard': 'Merapi/Data/merapi_krb.shp',
                'function': 'Volcano Building Impact',
            }
        }
        self.assertDictEqual(myExpectedDictionary, myDictionary)

    # def testAppendRow(self):
    #     """Test appendRow() functionality"""
    #     myTable = QTableWidget(PARENT)
    #     myTable.clearContents()
    #
    #     appendRow(myTable, 'Foo1', 'bar.py')
    #     appendRow(myTable, 'Foo2', {'number': 70})
    #
    #     self.assertEquals(myTable.rowCount(), 2, "row count don't match")
    #
    #     myItem = myTable.item(0, 0)
    #     myVariant = myItem.data(Qt.UserRole)
    #     myValue = myVariant.toPyObject()[0]
    #
    #     self.assertEquals(myValue, 'bar.py', " value dont' match")

        # myItem = myTable.item(1, 0)
        # myVariant = myItem.data(Qt.UserRole)
        # myValue = myVariant.toPyObject()[0]
        #
        # self.assertDictEqual(myValue, {'number': 70})

    def test_getPDFReportPath(self):
        """Test getPDFReport functionality"""
        myDialog = BatchRunner(PARENT, IFACE)
        myValue = myDialog.getPDFReportPath('/home/foo', 'bar')

        # we use os.path.join instead of hardcoded '/'
        myMapPath = os.path.join('/home/foo', 'bar.pdf')
        myTablePath = os.path.join('/home/foo', 'bar_table.pdf')
        myExpectedValue = (myMapPath, myTablePath)

        self.assertTupleEqual(myValue, myExpectedValue)


if __name__ == '__main__':
    suite = unittest.makeSuite(ScriptDialogTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
