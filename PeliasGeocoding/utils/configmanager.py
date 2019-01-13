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

import yaml

from PeliasGeocoding import PROVIDERS


def read_config():
    """
    Reads providers.yml from file and returns the parsed dict.

    :returns: Parsed settings dictionary.
    :rtype: dict
    """

    with open(PROVIDERS) as f:
        doc = yaml.safe_load(f)

    return doc


def write_config(new_config):
    """
    Dumps new config

    :param new_config: new provider settings after altering in dialog.
    :type new_config: dict
    """
    with open(PROVIDERS, 'w') as f:
        yaml.safe_dump(new_config, f)
