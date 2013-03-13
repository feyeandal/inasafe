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
from safe_qgis.utilities import which

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
              theCellSize,
              theExtent=None,
              theValue=1,
              theAttribute=None,
              theExtraKeywords=None):
    """Rasterizes a polygon layer to the extents and cell size provided.
     The layer must be a vector layer or an exception will be thrown.

    The output layer will always be in WGS84/Geographic.

    Args:

        * theLayer - a valid QGIS vector layer in EPSG:4326
        * theCellSize: Cell size for the output dataset in EPSG:4326 with
            the assumption that X and Y dimensions are identical.
        * theExtent (Optional) either:
            * an array representing the layer extents in the form [xmin, ymin,
                xmax, ymax]. It is assumed that the coordinates are in
                EPSG:4326 although currently no checks are made to enforce
                this.
            * or: A QgsGeometry of type polygon. Note that only the bounding
                box of the polygon will be used.
            Note: If no extent is specified, the extents of the polygon layer
            will be used.
        * theValue (Optional, defaults to 1): float - value to assign the
            polygonal areas in the output raster
        * theAttribute: string - field name in the input dataset that
            provdes the value that should be assigned to each polygon. Note
            that if theAttribute is set, theValue will be ignored.
        * theExtraKeywords - any additional keywords over and above the
          original keywords that should be associated with the cliplayer.

    Returns:
        Path to the output rasterized layer (placed in the system temp dir).

    Raises:
       None

    Rasterization will be performed using gdal_rasterize using a similar
    technique to this:

    gdal_rasterize -ts 24 23 -burn 1 -a_nodata -9999.5 -ot Float32 \
                -l flood_polygons flood_polygons.shp /tmp/test2.tif

    Where options provided have the following significance:

        * -ts 24 23 : Output image dimensions (we will need to compute this
            from theCellSise and theExtent
        * -burn 1 : Pixel value to be assigned where ever a polygon exists (1)
        * -a_nodata -9999.5: Value to assign for no data cells (-9999.5)
        * -ot Byte : output format for the resulting raster (Byte)
        * -l flood_polygons : layer name of input file to use (for shp set it
            to the filename sans '.shp')
        * flood_polygons.shp : input vector layer
        * /tmp/test.tif : output raster layer (does not need to preexist in
            gdal > 1.8)

    """
    #raise NotImplementedError

    if not theLayer:
        myMessage = tr('Layer passed to rasterize is None.')
        raise InvalidParameterError(myMessage)

    if theLayer.type() != QgsMapLayer.VectorLayer:
        myMessage = tr('Expected a vector layer but received a %s.' %
                       str(theLayer.type()))
        raise InvalidParameterError(myMessage)

    myAllowedTypes = [QGis.WKBPolygon, QGis.WKBPolygon25D]

    if theLayer.wkbType() not in myAllowedTypes:
        myMessage = tr('Expected a polygon layer but received a %s.' %
                       str(theLayer.wkbType()))
        raise InvalidParameterError(myMessage)

    myHandle, myFilename = tempfile.mkstemp('.tif', 'rasterize_', temp_dir())

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

    if type(theExtent) is list:
        myRect = QgsRectangle(theExtent[0], theExtent[1],
                              theExtent[2], theExtent[3])
        myClipPolygon = QgsGeometry.fromRect(myRect)
    elif (type(theExtent) is QgsGeometry and
            theExtent.wkbType in myAllowedTypes):
        myRect = theExtent.boundingBox().toRectF()
        myClipPolygon = theExtent
    else:
        # Extent is not required
        myClipPolygon = None

    if myClipPolygon is not None:
        myProjectedExtent = myXForm.transformBoundingBox(myRect)
    else:
        myProjectedExtent = None

    # Get vector layer
    myProvider = theLayer.dataProvider()
    if myProvider is None:
        myMessage = tr('Could not obtain data provider from '
                       'layer "%s"' % theLayer.source())
        raise Exception(myMessage)

    # Get the layer field list
    myAttributes = myProvider.attributeIndexes()
    myFieldList = myProvider.fields()

    # work out the layer name
    mySource = str(theLayer.source())
    myBase = os.path.basename(mySource)
    myBase = os.path.splitext(myBase)[0]

    myBinaryList = which('gdal_rasterize')
    if len(myBinaryList) < 1:
        raise CallGDALError(
            tr('gdal_rasterize could not be found on your computer'))
        # Use the first matching gdalwarp found
    myBinary = myBinaryList[0]

    myCommand = (
        '%(binary)s -ts 24 23 -burn %(value)s -a_nodata -9999.5 -ot '
        'Float32 -l %(layer)s %(in_file)s %(out_file)s' % {
        'binary': myBinary,
        'value': theValue,
        'layer': myBase,
        'in_file': theLayer.source(),
        'out_file': myFilename})
    LOGGER.debug(myCommand)
    myResult = QProcess().execute(myCommand)

    # For QProcess exit codes see
    # http://qt-project.org/doc/qt-4.8/qprocess.html#execute
    if myResult == -2:  # cannot be started
        myMessageDetail = tr('Process could not be started.')
        myMessage = tr(
            '<p>Error while executing the following shell command:'
            '</p><pre>%s</pre><p>Error message: %s'
            % (myCommand, myMessageDetail))
        raise CallGDALError(myMessage)
    elif myResult == -1:  # process crashed
        myMessageDetail = tr('Process could not be started.')
        myMessage = tr('<p>Error while executing the following shell command:'
                       '</p><pre>%s</pre><p>Error message: %s'
                       % (myCommand, myMessageDetail))
        raise CallGDALError(myMessage)

    # copy over the keywords from the polygon layer to the raster layer
    myKeywordIO = KeywordIO()
    myKeywordIO.copyKeywords(theLayer, myFilename,
                             theExtraKeywords=theExtraKeywords)

    return myFilename  # Filename of created file

