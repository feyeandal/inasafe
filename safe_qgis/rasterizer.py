"""InaSAFE Disaster risk assessment tool developed by AusAid -
  **ISClipper implementation.**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by
   the Free Software Foundation; either version 2 of the License, or
   (at your option) any later version.

"""

__author__ = 'tim@linfiniti.com'
__revision__ = '$Format:%H$'
__date__ = '20/01/2011'
__copyright__ = 'Copyright 2012, Australia Indonesia Facility for '
__copyright__ += 'Disaster Reduction'

import os
import sys
import tempfile
import logging

from PyQt4.QtCore import QCoreApplication, QProcess
from qgis.core import (QGis,
                       QgsCoordinateTransform,
                       QgsCoordinateReferenceSystem,
                       QgsRectangle,
                       QgsMapLayer,
                       QgsFeature,
                       QgsVectorFileWriter,
                       QgsGeometry)

from safe.common.utilities import temp_dir
from safe_qgis.safe_interface import (verify,
                                      readKeywordsFromFile)

from safe_qgis.keyword_io import KeywordIO
from safe_qgis.exceptions import (InvalidParameterError,
                                  NoFeaturesInExtentError,
                                  CallGDALError,
                                  InvalidProjectionError,
                                  InvalidClipGeometryError)

LOGGER = logging.getLogger(name='InaSAFE')


def tr(theText):
    """We define a tr() alias here since the ClipperTest implementation below
    is not a class and does not inherit from QObject.

    .. note:: see http://tinyurl.com/pyqt-differences

    Args:
       theText - string to be translated

    Returns:
       Translated version of the given string if available, otherwise
       the original string.
    """
    myContext = "@default"
    return QCoreApplication.translate(myContext, theText)


def rasterize(theLayer,
                     theExtent,
                     theCellSize,
                     theExtraKeywords=None,
                     theExplodeFlag=True,
                     theHardClipFlag=False):
    """Rasterizes a polygon layer to the extents and cell size provided.
     The layer must be a vector layer or an exception will be thrown.

    The output layer will always be in WGS84/Geographic.

    Args:

        * theLayer - a valid QGIS vector layer in EPSG:4326
        * theExtent either: an array representing the exposure layer
           extents in the form [xmin, ymin, xmax, ymax]. It is assumed
           that the coordinates are in EPSG:4326 although currently
           no checks are made to enforce this.
                    or: A QgsGeometry of type polygon. **Polygon clipping is
           currently only supported for vector datasets.**
        * theCellSize: Cell size for the output dataset in EPSG:4326 with
            the assumption that X and Y dimensions are identical.
        * theExtraKeywords - any additional keywords over and above the
          original keywords that should be associated with the cliplayer.
        * theHardClipFlag - a bool specifying whether line and polygon features
            that extend beyond the extents should be clipped such that they
            are reduced in size to the part of the geometry that intersects
            the extent only. Default is False.

    Returns:
        Path to the output rasterized layer (placed in the system temp dir).

    Raises:
       None

    """
    raise NotImplementedError

    if not theLayer or not theExtent:
        myMessage = tr('Layer or Extent passed to rasterize is None.')
        raise InvalidParameterError(myMessage)

    if theLayer.type() != QgsMapLayer.VectorLayer:
        myMessage = tr('Expected a vector layer but received a %s.' %
                       str(theLayer.type()))
        raise InvalidParameterError(myMessage)

    #myHandle, myFilename = tempfile.mkstemp('.sqlite', 'clip_',
    #    temp_dir())
    myHandle, myFilename = tempfile.mkstemp('.shp', 'clip_',
                                            temp_dir())

    # Ensure the file is deleted before we try to write to it
    # fixes windows specific issue where you get a message like this
    # ERROR 1: c:\temp\inasafe\clip_jpxjnt.shp is not a directory.
    # This is because mkstemp creates the file handle and leaves
    # the file open.
    os.close(myHandle)
    os.remove(myFilename)

    # Get the clip extents in the layer's native CRS
    myGeoCrs = QgsCoordinateReferenceSystem()
    myGeoCrs.createFromId(4326, QgsCoordinateReferenceSystem.EpsgCrsId)
    myXForm = QgsCoordinateTransform(myGeoCrs, theLayer.crs())
    myAllowedClipTypes = [QGis.WKBPolygon, QGis.WKBPolygon25D]
    if type(theExtent) is list:
        myRect = QgsRectangle(theExtent[0], theExtent[1],
                              theExtent[2], theExtent[3])
        myClipPolygon = QgsGeometry.fromRect(myRect)
    elif (type(theExtent) is QgsGeometry and
                  theExtent.wkbType in myAllowedClipTypes):
        myRect = theExtent.boundingBox().toRectF()
        myClipPolygon = theExtent
    else:
        raise InvalidClipGeometryError(
            tr('Clip geometry must be an extent or a single part'
               'polygon based geometry.'))

    myProjectedExtent = myXForm.transformBoundingBox(myRect)

    # Get vector layer
    myProvider = theLayer.dataProvider()
    if myProvider is None:
        myMessage = tr('Could not obtain data provider from '
                       'layer "%s"' % theLayer.source())
        raise Exception(myMessage)

    # Get the layer field list, select by our extent then write to disk
    # .. todo:: FIXME - for different geometry types we should implement
    #    different clipping behaviour e.g. reject polygons that
    #    intersect the edge of the bbox. Tim
    myAttributes = myProvider.attributeIndexes()
    myFetchGeometryFlag = True
    myUseIntersectFlag = True
    myProvider.select(myAttributes,
                      myProjectedExtent,
                      myFetchGeometryFlag,
                      myUseIntersectFlag)

    myFieldList = myProvider.fields()

    myWriter = QgsVectorFileWriter(myFilename,
                                   'UTF-8',
                                   myFieldList,
                                   theLayer.wkbType(),
                                   myGeoCrs,
                                   'ESRI Shapefile')
    if myWriter.hasError() != QgsVectorFileWriter.NoError:
        myMessage = tr('Error when creating shapefile: <br>Filename:'
                       '%s<br>Error: %s' %
                       (myFilename, myWriter.hasError()))
        raise Exception(myMessage)

    # Reverse the coordinate xform now so that we can convert
    # geometries from layer crs to geocrs.
    myXForm = QgsCoordinateTransform(theLayer.crs(), myGeoCrs)
    # Retrieve every feature with its geometry and attributes
    myFeature = QgsFeature()
    myCount = 0
    while myProvider.nextFeature(myFeature):
        myGeometry = myFeature.geometry()
        # Loop through the parts adding them to the output file
        # we write out single part features unless theExplodeFlag is False
        if theExplodeFlag:
            myGeometryList = explodeMultiPartGeometry(myGeometry)
        else:
            myGeometryList = [myGeometry]

        for myPart in myGeometryList:
            myPart.transform(myXForm)
            if theHardClipFlag:
                # Remove any dangling bits so only intersecting area is
                # kept.
                myPart = clipGeometry(myClipPolygon, myPart)
            if myPart is None:
                continue
            myFeature.setGeometry(myPart)
            myWriter.addFeature(myFeature)
        myCount += 1
    del myWriter  # Flush to disk

    if myCount < 1:
        myMessage = tr('No features fall within the clip extents. '
                       'Try panning / zooming to an area containing data '
                       'and then try to run your analysis again.'
                       'If hazard and exposure data doesn\'t overlap '
                       'at all, it is not possible to do an analysis.'
                       'Another possibility is that the layers do overlap '
                       'but because they may have different spatial '
                       'references, they appear to be disjoint. '
                       'If this is the case, try to turn on reproject '
                       'on-the-fly in QGIS.')
        raise NoFeaturesInExtentError(myMessage)

    myKeywordIO = KeywordIO()
    myKeywordIO.copyKeywords(theLayer, myFilename,
                             theExtraKeywords=theExtraKeywords)

    return myFilename  # Filename of created file

