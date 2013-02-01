"""
InaSAFE Disaster risk assessment tool developed by AusAid and World Bank
- **Script runner test cases.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__date__ = '1/02/2013'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import unittest
# Needed though not used below
from PyQt4.QtGui import QApplication  # pylint: disable=W0611
from safe_qgis.utilities_test import getQgisTestApp

QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()

from script_dialog import readScenarios

class ScriptDialogTest(unittest.TestCase):

    def testScenarioParser(self):
        """Test if we can load scenarios from a text file."""
        myDictionary = readScenarios('test.txt')
        myExpectedDictionary = {}
        self.assertDictEqual(myExpectedDictionary, myDictionary)

if __name__ == '__main__':
    suite = unittest.makeSuite(ScriptDialogTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
