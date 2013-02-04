"""
InaSAFE Disaster risk assessment tool developed by AusAid -
**Script to run jakarta flood scenariol**

Contact : ole.moller.nielsen@gmail.com

.. note:: This program is free software; you can redistribute it and/or modify
     it under the terms of the GNU General Public License as published by
     the Free Software Foundation; either version 2 of the License, or
     (at your option) any later version.

"""

__author__ = 'bungcip@gmail.com'
__revision__ = '$Format:%H$'
__date__ = '10/10/2012'
__copyright__ = ('Copyright 2012, Australia Indonesia Facility for '
                 'Disaster Reduction')

import os
import safe_qgis.macro as macro


def runScript():
    myRoot = os.path.abspath(os.path.join(os.path.realpath(os.path.dirname(
        __file__)),
          '..',
          '..',
          'inasafe_data'))

    macro.addLayers(myRoot, [
        'exposure/DKI_Buildings.shp',
        'hazard/Jakarta_RW_2007flood.shp',
        'test/Population_Jakarta_geographic.asc',
    ])

    macro.runScenario()
