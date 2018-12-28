# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PeliasGeocoding
                                 A QGIS plugin
 QGIS plugin to query Pelias endpoints from configurable sources.
                             -------------------
        begin                : 2019-01-05
        copyright            : (C) 2019 by Nils Nolde
        email                : nils@gis-ops.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.core import (QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsProject
                       )

def transformToWGS(old_crs):
    """
    Returns a transformer to WGS84

    :param old_crs: CRS to transfrom from
    :type old_crs: QgsCoordinateReferenceSystem

    :returns: transformer to use in various modules.
    :rtype: QgsCoordinateTransform
    """

    outCrs = QgsCoordinateReferenceSystem(4326)
    xformer = QgsCoordinateTransform(old_crs, outCrs, QgsProject.instance())

    return xformer
