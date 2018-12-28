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

LAYERS = [
    'venue',
    'address',
    'street',
    'neighbourhood',
    'borough',
    'localadmin	',
    'locality',
    'county',
    'macrocounty',
    'region',
    'macroregion',
    'country',
    'coarse'
]

SOURCES = [
    'osm',
    'oa',
    'wof',
    'gn'
]