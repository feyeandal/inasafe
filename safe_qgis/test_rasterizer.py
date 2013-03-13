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

from qgis.core import (QgsVectorLayer,
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
VECTOR_PATH = os.path.join(UNITDATA, 'hazard', 'flood_polygons.shp')

# Handle to common QGis test app
QGISAPP, CANVAS, IFACE, PARENT = getQgisTestApp()


class RasterizerTest(unittest.TestCase):
    """Test the InaSAFE Rasterizer"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_rasterize(self):
        """Vector polygon layer can be rasterized
        """
        # Create a vector layer
        myName = 'flood_polygons'
        myVectorLayer = QgsVectorLayer(VECTOR_PATH, myName, 'ogr')

        myMessage = 'Did not find layer "%s" in path "%s"' % (myName,
                                                              VECTOR_PATH)
        assert myVectorLayer is not None, myMessage
        myMessage = 'Layer "%s" in path "%s" is not valid' % (myName,
                                                              VECTOR_PATH)
        assert myVectorLayer.isValid(), myMessage
        # Create a bounding box
        myRect = [106.9041416, -6.3027378, 106.9211015, -6.2843478]

        # rasterize the vector to the bbox
        myResult = rasterize(myVectorLayer,
                             theCellSize=0.000706662322222,
                             theRect=myRect,
                             theValue=1,
                             theAttribute=None,
                             theExtraKeywords=None,
                             theExplodeFlag=True,
                             theHardClipFlag=False)

        # Check the output is valid
        with RedirectStdStreams(stdout=DEVNULL, stderr=DEVNULL):
            myRasterLayer = QgsRasterLayer(myResult, 'rasterized_ouput')
        myMessage = ('Rasterised output is not a valid raster layer. %s' % (
            myResult))
        assert myRasterLayer.isValid(), myMessage

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

    def test_vectorProjections(self):
        """Test vector input data is reprojected properly during rasterize.
        """
        raise NotImplementedError
        # Input data is OSM in GOOGLE CRS
        # We are reprojecting to GEO and expecting the output shp to be in GEO
        # see https://github.com/AIFDR/inasafe/issues/119
        # and https://github.com/AIFDR/inasafe/issues/95
        myVectorLayer = QgsVectorLayer(VECTOR_PATH2,
                                       'OSM Buildings',
                                       'ogr')
        myMessage = 'Failed to load osm buildings'
        assert myVectorLayer is not None, myMessage
        assert myVectorLayer.isValid()
        setCanvasCrs(GEOCRS, True)
        setJakartaGeoExtent()
        myClipRect = [106.52, -6.38, 107.14, -6.07]
        # Clip the vector to the bbox
        myResult = rasterizeLayer(myVectorLayer, myClipRect)
        assert(os.path.exists(myResult))


if __name__ == '__main__':
    suite = unittest.makeSuite(RasterizerTest, 'test')
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)
