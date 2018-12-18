# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PeliasTools
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

from qgis.core import QgsApplication

from .gui import PeliasToolsDialog
# from .proc import provider


class PeliasTools():
    """QGIS Plugin Implementation."""
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        self.dialog = PeliasToolsDialog.PeliasToolsDialogMain(iface)
        # self.provider = provider.ORStoolsProvider()

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        # QgsApplication.processingRegistry().addProvider(self.provider)
        self.dialog.initGui()
        
    def unload(self):
        """remove menu entry and toolbar icons"""
        # if self.provider:
        #     QgsApplication.processingRegistry().removeProvider(self.provider)
        self.dialog.unload()