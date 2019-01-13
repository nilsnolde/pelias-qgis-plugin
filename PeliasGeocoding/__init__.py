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

import os.path
import configparser
from datetime import datetime


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load PeliasTools plugin class .

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """

    from .PeliasToolsPlugin import PeliasTools
    return PeliasTools(iface)


# Define plugin wide constants
PLUGIN_NAME = 'Pelias Geocoding'
DEFAULT_COLOR = '#a8b1f5'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCE_PREFIX = ":plugins/PeliasTools/gui/img/"
PROVIDERS = os.path.join(BASE_DIR, 'providers.yml')

# Read config.ini
CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(BASE_DIR, 'config.ini'))

# Read metadata.txt
METADATA = configparser.ConfigParser()
METADATA.read(os.path.join(BASE_DIR, 'metadata.txt'))
today = datetime.today()

__version__ = METADATA['general']['version']
__author__ = METADATA['general']['author']
__email__ = METADATA['general']['email']
__web__ = METADATA['general']['homepage']
__help__ = METADATA['general']['help']
__date__ = today.strftime('%Y-%m-%d')
__copyright__ = '(C) {} by {}'.format(today.year, __author__)
