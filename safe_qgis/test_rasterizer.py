"""
InaSAFE Disaster risk assessment tool developed by AusAid -
 **Rasterizer test suite.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""
__author__ = 'tim@linfiniti.com'
__date__ = '20/01/2011'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

#from unittest import expectedFailure
import unittest
import sys
import os

# Add PARENT directory to path to make test aware of other modules
pardir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(pardir)

import numpy

from qgis.core import (
    QGis,
    QgsVectorLayer,
    QgsRasterLayer,
    QgsGeometry,
    QgsPoint)

from safe_qgis.safe_interface import readSafeLayer
from safe_qgis.safe_interface import getOptimalExtent
from safe_qgis.exceptions import InvalidProjectionError, CallGDALError
from safe_qgis.rasterizer import rasterize
from safe_qgis.utilities import qgisVersion

from safe_qgis.utilities_test import (getQgisTestApp,
                                      setCanvasCrs,
                                      RedirectStdStreams,
                                      DEVNULL,
                                      GEOCRS)

from safe.common.testing import UNITDATA
from safe.common.exceptions import GetDataError

# Setup pathnames for test data sets
VECTOR_PATH = os.path.join(UNITDATA, 'hazard', 'jk_flood_polygons.shp')
RASTER_PATH = os.path.join(UNITDATA, 'exposure', 'jk_population.shp')

# Handle to common QGis test app
QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()


class RasterizerTest(unittest.TestCase):
    """Test the InaSAFE Rasterizer"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def loadVectorLayer(self):
        """Helper function to load the vector layer."""
        # Create a vector layer
        myName = 'flood_polygons'
        myVectorLayer = QgsVectorLayer(VECTOR_PATH, myName, 'ogr')

        myMessage = 'Did not find layer "%s" in path "%s"' % (myName,
                                                              VECTOR_PATH)
        assert myVectorLayer is not None, myMessage

        myMessage = 'Expected layer to be of type polygon, ' \
                    'got %s' % myVectorLayer.wkbType()
        self.assertEqual(myVectorLayer.wkbType(), QGis.WKBPolygon, myMessage)

        myMessage = ('Layer "%s" in path "%s" valid flag is %s' % (
            myName,
            VECTOR_PATH,
            myVectorLayer.isValid()))

        assert myVectorLayer.isValid(), myMessage
        return myVectorLayer

    def checkRaster(self, theRaster):
        """Helper function to check the created raster is OK."""
        with RedirectStdStreams(stdout=DEVNULL, stderr=DEVNULL):
            myRasterLayer = QgsRasterLayer(theRaster, 'rasterized_ouput')
        myMessage = ('Rasterised output is not a valid raster layer. %s' % (
            theRaster))
        assert myRasterLayer.isValid(), myMessage

    def test_rasterize_with_value(self):
        """Vector polygon layer can be rasterized, giving it a fixed value.
        """
        myVectorLayer = self.loadVectorLayer()

        # rasterize the vector to the bbox
        myResult = rasterize(myVectorLayer,
                             theCellSize=0.000706662322222,
                             theValue=1,
                             theAttribute=None,
                             theExtraKeywords=None)
        # Check the output is valid
        self.checkRaster(myResult)

    def test_rasterize_with_attribute(self):
        """Vector polygon layer can be rasterized, fgiving it an attribute."""
        myVectorLayer = self.loadVectorLayer()
        # rasterize the vector to the bbox
        myResult = rasterize(myVectorLayer,
                             theCellSize=0.000706662322222,
                             theAttribute='depth',
                             theExtraKeywords=None)
        # Check the output is valid
        self.checkRaster(myResult)

    def test_invalidFilenamesCaught(self):
        """Invalid filenames raise appropriate exceptions

        Wrote this test because test_rasterizeBoth raised the wrong error
        when file was missing. Instead of reporting that, it gave
        Western boundary must be less than eastern. I got [0.0, 0.0, 0.0, 0.0]

        See issue #170
        """
        raise NotImplementedError
        # Try to create a vector layer from non-existing filename
        myName = 'stnhaoeu_78oeukqjkrcgA'
        myPath = 'OEk_tnshoeu_439_kstnhoe'

        with RedirectStdStreams(stdout=DEVNULL, stderr=DEVNULL):
            myVectorLayer = QgsVectorLayer(myPath, myName, 'ogr')

        myMessage = ('QgsVectorLayer reported "valid" for non '
                     'existent path "%s" and name "%s".'
                     % (myPath, myName))
        assert not myVectorLayer.isValid(), myMessage

        # Create a raster layer
        with RedirectStdStreams(stdout=DEVNULL, stderr=DEVNULL):
            myRasterLayer = QgsRasterLayer(myPath, myName)
        myMessage = ('QgsRasterLayer reported "valid" for non '
                     'existent path "%s" and name "%s".'
                     % (myPath, myName))
        assert not myRasterLayer.isValid(), myMessage


if __name__ == '__main__':
    suite = unittest.makeSuite(RasterizerTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
