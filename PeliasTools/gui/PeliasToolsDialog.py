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

import os
import webbrowser

from PyQt5.QtWidgets import (QAction,
                             QDialog,
                             QApplication,
                             QComboBox,
                             QPushButton,
                             QMenu,
                             QMessageBox)
from PyQt5.QtCore import Qt, QVariant
from PyQt5.QtGui import QPixmap, QIcon
from qgis.core import (QgsProject,
                       QgsMapLayer,
                       QgsWkbTypes,
                       QgsMapLayerProxyModel
                       )

from PeliasTools import PLUGIN_NAME, ICON_DIR, DEFAULT_COLOR, __email__, __web__, __version__, __help__
from .PeliasMainUI import Ui_PeliasMainDialog
from PeliasTools.utils import maptools


# def on_config_click(parent):
#     """Pop up config window. Outside of classes because it's accessed by both.
#     """
#     config_dlg = ORStoolsDialogConfigMain(parent=parent)
#     config_dlg.exec_()
#
#
def on_help_click():
    webbrowser.open(__help__)


class PeliasToolsDialogMain:
    """Defines all mandatory QGIS things about dialog."""

    def __init__(self, iface):
        """

        :param iface: the current QGIS interface
        :type iface: Qgis.Interface
        """
        self.iface = iface
        self.project = QgsProject.instance()

        self.first_start = True
        # Dialogs
        self.dlg = None
        self.advanced = None
        self.menu = None
        self.actions = None

    def initGui(self):
        def create_icon(f):
            return QIcon(os.path.join(ICON_DIR, f))

        icon_plugin = create_icon('plugin_icon.png')

        self.actions = [
            QAction(
                icon_plugin,
                PLUGIN_NAME,  # tr text
                self.iface.mainWindow()  # parent
            ),
            # # Config dialog
            # QAction(
            #     create_icon('icon_settings.svg'),
            #     'Configuration',
            #     self.iface.mainWindow()
            # ),
            # # About dialog
            # QAction(
            #     create_icon('icon_about.png'),
            #     'About',
            #     self.iface.mainWindow()
            # ),
            # Help page
            QAction(
                create_icon('icon_help.png'),
                'Help',
                self.iface.mainWindow()
            )

        ]

        # Create menu
        self.menu = QMenu(PLUGIN_NAME)
        self.menu.setIcon(icon_plugin)
        self.menu.addActions(self.actions)

        # Add menu to Web menu and icon to toolbar
        self.iface.webMenu().addMenu(self.menu)
        self.iface.addWebToolBarIcon(self.actions[0])

        # Connect slots to events
        self.actions[0].triggered.connect(self.run)
        self.actions[1].triggered.connect(on_help_click)
        # self.actions[1].triggered.connect(lambda: on_config_click(parent=self.iface.mainWindow()))
        # Connect other dialogs
        # self.actions[2].triggered.connect(self._on_about_click)

    def unload(self):
        self.iface.webMenu().removeAction(self.menu.menuAction())
        self.iface.removeWebToolBarIcon(self.actions[0])
        QApplication.restoreOverrideCursor()
        del self.dlg

    def _on_about_click(self):
        info = '<b>Pelias Tools</b> provides access to <a href="https://github.com/pelias/pelias" style="color: {0}">Pelias</a> geocoding functionalities.<br><br>' \
               'Author: Nils Nolde<br>' \
               'Email: <a href="mailto:Nils Nolde <{1}>">{1}</a><br>' \
               'Web: <a href="{2}">{2}</a><br>' \
               'Repo: <a href="https://github.com/nilsnolde/ORStools">github.com/nilsnolde/ORStools</a><br>' \
               'Version: {3}'.format(DEFAULT_COLOR, __email__, __web__, __version__)

        QMessageBox.information(
            self.iface.mainWindow(),
            'About {}'.format(PLUGIN_NAME),
            info
        )

    # @staticmethod
    # def get_quota():
    #     """Update remaining quota from env variables"""
    #     # Dirty hack out of laziness.. Prone to errors
    #     text = []
    #     for var in sorted(ENV_VARS.keys(), reverse=True):
    #         text.append(os.environ[var])
    #     return '/'.join(text)

    def run(self):
        # Only populate GUI if it's the first start of the plugin within the QGIS session
        # If not checked, GUI would be rebuilt every time!
        if self.first_start:
            self.first_start = False
            self.dlg = PeliasToolsDialog(self.iface, self.iface.mainWindow())  # setting parent enables modal view

        self.dlg.show()
        result = self.dlg.exec()
        if result:
            pass


class PeliasToolsDialog(QDialog, Ui_PeliasMainDialog):
    """Define the custom behaviour of Dialog"""

    def __init__(self, iface, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.iface = iface
        self.project = QgsProject.instance()  # invoke a QgsProject instance
        self.last_maptool = self.iface.mapCanvas().mapTool()

        # # Set up env variables for remaining quota
        # os.environ["ORS_QUOTA"] = "None"
        # os.environ["ORS_REMAINING"] = "None"

        # Programmtically invoke ORS logo
        # header_pic = QPixmap(os.path.join(ICON_DIR, "openrouteservice.png"))
        # pixmap = header_pic.scaled(150, 50,
        #                            aspectRatioMode=Qt.KeepAspectRatio,
        #                            transformMode=Qt.SmoothTransformation
        #                            )
        # self.header_pic.setPixmap(pixmap)
        # Settings button icon
        # self.config_button.setIcon(QIcon(os.path.join(ICON_DIR, 'icon_settings.svg')))
        self.help_button.setIcon(QIcon(os.path.join(ICON_DIR, 'icon_help.png')))

        #### Set up signals/slots ####

        # Config/Help dialogs
        # self.config_button.clicked.connect(lambda: on_config_click(self))
        self.help_button.clicked.connect(on_help_click)
        self.search_focus_button.clicked.connect(self._on_map_click)
        self.search_rest_circle_button.clicked.connect(self._on_map_click)


    def _on_map_click(self):
        """
        Initialize the mapTool to select coordinates in map canvas.
        """

        self.showMinimized()
        sending_button = self.sender().objectName()
        self.mapTool = maptools.PointTool(self.iface.mapCanvas(), sending_button)
        self.iface.mapCanvas().setMapTool(self.mapTool)
        self.mapTool.canvasClicked.connect(self._writeCoordinateLabel)

    # Write map coordinates to text fields
    def _writeCoordinateLabel(self, point, button):
        """
        Writes the selected coordinates from map canvas to its accompanying label.

        :param point: Point selected with mapTool.
        :type point: QgsPointXY

        :param button: Button name which intialized mapTool.
        :param button: str
        """

        x, y = point

        if button == self.search_focus_button.objectName():
            self.search_focus_x.setText("{0:.6f}".format(x))
            self.search_focus_y.setText("{0:.6f}".format(y))

        if button == self.search_rest_circle_button.objectName():
            self.search_rest_circle_x.setText("{0:.6f}".format(x))
            self.search_rest_circle_y.setText("{0:.6f}".format(y))

        # Restore old behavior
        QApplication.restoreOverrideCursor()
        self.mapTool.canvasClicked.disconnect()
        self.iface.mapCanvas().setMapTool(self.last_maptool)
        if self.windowState() == Qt.WindowMinimized:
            # Window is minimised. Restore it.
            self.setWindowState(Qt.WindowMaximized)
            self.activateWindow()