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

import webbrowser

from PyQt5.QtWidgets import (QAction,
                             QDialog,
                             QApplication,
                             QInputDialog,
                             QMenu,
                             QMessageBox,
                             QToolBar)
from PyQt5.QtCore import QVariant
from PyQt5.QtGui import QPixmap, QIcon
from qgis.core import (QgsProject,
                       QgsField)
from qgis.gui import QgsFilterLineEdit, QgsCollapsibleGroupBox
import processing
from . import resources_rc

from .PeliasMainUI import Ui_PeliasMainDialog
from .PeliasToolsDialogConfig import PeliasToolsDialogConfigMain
from PeliasGeocoding import PLUGIN_NAME, RESOURCE_PREFIX, DEFAULT_COLOR, __email__, __web__, __version__, __help__
from PeliasGeocoding.core import client, response_handler
from PeliasGeocoding.utils import maptools, configmanager, logger, exceptions


def on_help_click():
    """Open help URL from button/menu entry."""
    webbrowser.open(__help__)

def on_config_click(parent):
    """Pop up provider config window. Outside of classes because it's accessed by multiple dialogs.

    :param parent: Sets parent window for modality.
    :type parent: QDialog
    """

    config_dlg = PeliasToolsDialogConfigMain(parent=parent)
    config_dlg.exec_()


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
        self.toolbar = None
        self.actions = None

        # Quick reverse tools
        self.last_maptool = None
        self.point_tool = None

    def initGui(self):
        """Called when plugin is activated (on QGIS startup or when activated in Plugin Manager)."""

        def create_icon(f):
            """
            internal function to create action icons

            :param f: file name of icon.
            :type f: str

            :returns: icon object to insert to QAction
            :rtype: QIcon
            """
            return QIcon(RESOURCE_PREFIX + f)

        icon_plugin = create_icon('icon_plugin.svg')

        self.actions = [
            QAction(
                icon_plugin,
                "Pelias Controls",  # tr text
                self.iface.mainWindow()  # parent
            ),
            # Quick search button
            QAction(
                QIcon(QPixmap(RESOURCE_PREFIX + 'icon_forward.svg')),
                'Quick Forward Geocode',
                self.iface.mainWindow()
            ),
            # Quick reverse button
            QAction(
                QIcon(QPixmap(RESOURCE_PREFIX + 'icon_reverse.svg')),
                'Quick Reverse Geocode',
                self.iface.mainWindow()
            ),
            # # Config dialog
            QAction(
                create_icon('icon_settings.png'),
                'Provder Configuration',
                self.iface.mainWindow()
            ),
            # Help
            QAction(
                create_icon('icon_help.png'),
                'Pelias Documentation',
                self.iface.mainWindow()
            ),
            # # About dialog
            QAction(
                create_icon('icon_about.png'),
                'About',
                self.iface.mainWindow()
            ),

        ]

        # Create menu
        self.menu = QMenu(PLUGIN_NAME)
        self.menu.setIcon(icon_plugin)
        self.menu.addActions(self.actions)

        # Add menu to Web menu and make sure it exsists and add icon to toolbar
        self.iface.addPluginToWebMenu("_tmp", self.actions[5])
        self.iface.webMenu().addMenu(self.menu)
        self.iface.removePluginWebMenu("_tmp", self.actions[5])

        self.toolbar = self.iface.addToolBar(u'PeliasGeocoding')
        self.toolbar.setObjectName(u'Pelias')
        self.toolbar.addAction(self.actions[0])
        self.toolbar.addAction(self.actions[1])
        self.toolbar.addAction(self.actions[2])
        self.iface.mainWindow().findChild(QToolBar, 'Pelias').setVisible(True)

        # Connect slots to events
        self.actions[0].triggered.connect(self.show_main_dialog)
        self.actions[1].triggered.connect(self._forward_geocode)
        self.actions[2].triggered.connect(self._init_reverse)
        self.actions[3].triggered.connect(lambda: on_config_click(parent=self.iface.mainWindow()))
        self.actions[4].triggered.connect(on_help_click)
        self.actions[5].triggered.connect(self._on_about_click)

    def unload(self):
        """Called when QGIS closes or plugin is deactivated in Plugin Manager"""

        self.iface.webMenu().removeAction(self.menu.menuAction())
        # self.iface.removeWebToolBarIcon(self.actions[0])
        # self.iface.removeWebToolBarIcon(self.actions[1])
        # self.iface.removeWebToolBarIcon(self.actions[2])
        QApplication.restoreOverrideCursor()
        del self.toolbar
        del self.dlg

    def _on_about_click(self):
        """Slot for click event of About button/menu entry."""

        info = '<b>Pelias Tools</b> provides access to <a href="https://github.com/pelias/pelias" style="color: {0}">Pelias</a> geocoding functionalities.<br><br>' \
               '<center><a href=\"https://gis-ops.com\"><img src=\":/plugins/PeliasTools/gui/img/logo_gisops_300.png\"/></a> <br><br></center>' \
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

    def _get_provider_input(self):
        """
        :returns: Returns selected provider from dropdown.
        :rtype: (dict, str, boolean)
        """

        providers = configmanager.read_config()['providers']
        providers_names = [provider['name'] for provider in providers]
        provider_name, ok = QInputDialog.getItem(self.iface.mainWindow(),
                                                "Pelias Providers",
                                                "Choose a provider",
                                                providers_names,
                                                0,
                                                False)
        return providers, provider_name, ok


    def _forward_geocode(self):
        """Performs quick forward geocoding"""

        address, ok = QInputDialog.getText(self.iface.mainWindow(),
                                        "Pelias Forward Geocoding",
                                        "Enter an address")
        if not ok:
            return

        providers, provider_name, ok = self._get_provider_input()
        if ok:
            provider = [provider for provider in providers if provider['name'] == provider_name][0]
            clnt = client.Client(provider)
            responsehandler = response_handler.ResponseHandler(QgsField('id', QVariant.String))
            response = clnt.request(provider['endpoints']['search'],
                                     {'text': address,
                                      'size': 5})
            layer_out = responsehandler.get_layer('search', response)
            layer_out.updateExtents()
            self.project.addMapLayer(layer_out)

    def _init_reverse(self):
        """Initializes reverse geocoding"""

        self.last_maptool = self.iface.mapCanvas().mapTool()

        self.point_tool = maptools.PointTool(self.iface.mapCanvas(), icon='icon_locate.png')
        self.iface.mapCanvas().setMapTool(self.point_tool)
        self.point_tool.canvasClicked.connect(self._reverse_geocode)

    def _reverse_geocode(self, point):
        """Performs reverse geocoding"""

        providers, provider_name, ok = self._get_provider_input()
        if ok:
            provider = [provider for provider in providers if provider['name'] == provider_name][0]
            clnt = client.Client(provider)
            responsehandler = response_handler.ResponseHandler(QgsField('id', QVariant.String))
            try:
                response = clnt.request(provider['endpoints']['reverse'],
                                         {'point.lat': point.y(),
                                          'point.lon': point.x(),
                                          'size': 5})
                layer_out = responsehandler.get_layer('reverse', response)
                layer_out.updateExtents()
                self.project.addMapLayer(layer_out)

            except:
                raise

            finally:
                QApplication.restoreOverrideCursor()
                self.point_tool.canvasClicked.disconnect()
                self.iface.mapCanvas().setMapTool(self.last_maptool)

    def _collect_base_params(self):
        """
        Collect all parameters common to all endpoints.

        :returns: Common parameters.
        :rtype: dict
        """
        params = dict()
        params['size'] = self.dlg.limit_value.value()

        if not (self.dlg.search_focus_y.isNull() or self.dlg.search_focus_x.isNull()) and  \
                self.dlg.search_focus_group.isEnabled():
            params['focus.point.lat'] = self.dlg.search_focus_y.value()
            params['focus.point.lon'] = self.dlg.search_focus_x.value()

        if not (self.dlg.search_rest_rect_xmin.isNull() or self.dlg.search_rest_rect_ymin.isNull() or
                self.dlg.search_rest_rect_xmax.isNull() or self.dlg.search_rest_rect_xmax.isNull()) and  \
                self.dlg.search_rest_rect_group.isEnabled():
            params['boundary.rect.min_lon'] = self.dlg.search_rest_rect_xmin.value()
            params['boundary.rect.min_lat'] = self.dlg.search_rest_rect_ymin.value()
            params['boundary.rect.max_lon'] = self.dlg.search_rest_rect_xmax.value()
            params['boundary.rect.max_lat'] = self.dlg.search_rest_rect_ymax.value()

        if not (self.dlg.search_rest_circle_x.isNull() or self.dlg.search_rest_circle_y.isNull()) and  \
               (self.dlg.search_rest_circle_x.isEnabled() and self.dlg.search_rest_circle_y.isEnabled()):
            params['boundary.circle.lon'] = self.dlg.search_rest_circle_x.value()
            params['boundary.circle.lat'] = self.dlg.search_rest_circle_y.value()
            params['boundary.circle.radius'] = self.dlg.search_rest_circle_value.value()

        if not self.dlg.search_rest_country.isNull():
            params['boundary.country'] = self.dlg.search_rest_country.value()

        if self.dlg.search_filters_sources_combo.checkedItems():
            params['sources'] = ",".join(self.dlg.search_filters_sources_combo.checkedItems())

        if self.dlg.search_filters_layer_combo.checkedItems():
            params['layers'] = ",".join(self.dlg.search_filters_layer_combo.checkedItems())

        return params

    def show_main_dialog(self):
        """Initializes main Pelias dialog window."""

        # Only populate GUI if it's the first start of the plugin within the QGIS session
        # If not checked, GUI would be rebuilt every time!
        if self.first_start:
            self.first_start = False

            self.dlg = PeliasToolsDialog(self.iface, self.iface.mainWindow())  # setting parent enables modal view
            self.dlg.buttonBox.accepted.disconnect(self.dlg.accept)
            self.dlg.buttonBox.accepted.connect(self._run_main_dialog)

            providers = configmanager.read_config()['providers']
            for provider in providers:
                self.dlg.provider_combo.addItem(provider['name'], provider)

        self.dlg.show()

    def _run_main_dialog(self):
        """Runs the main function when Apply is clicked."""

        self.dlg.debug_text.clear()

        provider = self.dlg.provider_combo.currentData()
        clnt = client.Client(provider=provider)  # provider object has all data from config.yml
        clnt_msg = ''

        # Notify user when query limit is reached
        sleep_notifier = "OverQueryLimit: Wait for {} seconds"
        clnt.overQueryLimit.connect(lambda sleep_for: self.dlg.debug_text.setText(sleep_notifier.format(str(sleep_for))))

        # Collect base parameters common for both endpoints
        params = self._collect_base_params()

        if self.dlg.search_tab.currentIndex() == 0:
            method = 'search'
            params['text'] = self.dlg.search_free_text.value()

        elif self.dlg.search_tab.currentIndex() == 1:
            method = 'structured'
            layers_list = self.dlg.layer_list
            for idx in range(layers_list.count()):
                item = layers_list.item(idx).text()
                param, value = item.split("=")
                params[param] = value

        elif self.dlg.search_tab.currentIndex() == 2:
            method = 'reverse'
            params['point.lon'] = self.dlg.reverse_x.value()
            params['point.lat'] = self.dlg.reverse_y.value()

        responsehandler = response_handler.ResponseHandler(QgsField('id', QVariant.String),
                                                           self.dlg.debug_check.isChecked())
        try:
            response = clnt.request(provider['endpoints'][method],
                                    params)
            layer_out = responsehandler.get_layer(method, response)
            layer_out.updateExtents()
            self.project.addMapLayer(layer_out)
        except exceptions.Timeout:
            msg = "The connection has timed out!"
            logger.log(msg, 2)
            self.dlg.debug_text.setText(msg)

        except (exceptions.ApiError,
                exceptions.InvalidKey,
                exceptions.GenericServerError) as e:

            msg = [e.__class__.__name__ ,
                   str(e)]
            logger.log("{}: {}".format(*msg), 2)
            clnt_msg += "<b>{}</b>: ({})<br>".format(*msg)

        except Exception as e:
            msg = [e.__class__.__name__ ,
                   str(e)]
            logger.log("{}: {}".format(*msg), 2)
            clnt_msg += "<b>{}</b>: {}<br>".format(*msg)
            raise

        finally:
            # Write some output
            if clnt.warnings is not None:
                for warning in clnt.warnings:
                    clnt_msg += "<b>Warning</b>: {}<br>".format(warning)
                    logger.log(warning, 1)

            clnt_msg += '<a href="{0}">{0}</a><br>'.format(clnt.url)
            self.dlg.debug_text.setHtml(clnt_msg)


class PeliasToolsDialog(QDialog, Ui_PeliasMainDialog):
    """Define the custom behaviour of Dialog, more Qt related"""

    def __init__(self, iface, parent=None):
        """
        :param iface: QGIS interface
        :type iface: QgisInterface

        :param parent: parent window for modality.
        :type parent: QDialog/QApplication
        """
        QDialog.__init__(self, parent)
        self.setupUi(self)

        self.iface = iface
        self.project = QgsProject.instance()  # invoke a QgsProject instance

        # enable functionality to select all text when in focus
        for lineedit_widget in self.findChildren(QgsFilterLineEdit):
            lineedit_widget.setSelectOnFocus(True)

        # Map Tools & other class-wide variables
        self.point_tool = None
        self.rect_tool = None
        self.last_maptool = self.iface.mapCanvas().mapTool()

        self.layer_list = self.search_struc_list
        self.clear_buttons = [self.search_rest_circle_clear,
                              self.search_rest_rect_clear,
                              self.search_focus_clear,
                              self.reverse_clear]

        # Disable components for
        # Collapse all QgsCollapsibleGroupBoxs
        collapsible_boxes = self.findChildren(QgsCollapsibleGroupBox)
        for box in collapsible_boxes:
            box.setCollapsed(True)

        #### Set up signals/slots ####
        # Tab widget to disable components for reverse..
        self.search_tab.currentChanged.connect(self._on_reverse_select)

        # Config/Help dialogs
        # self.config_button.clicked.connect(lambda: on_config_click(self))
        self.help_button.clicked.connect(on_help_click)
        self.provider_config.clicked.connect(lambda: on_config_click(self))
        self.provider_refresh.clicked.connect(self._on_prov_refresh_click)

        # Search Buttons
        self.search_focus_button.clicked.connect(self._on_point_click)
        self.search_rest_circle_button.clicked.connect(self._on_point_click)
        self.search_rest_rect_button.clicked.connect(self._on_rect_click)
        for button in self.clear_buttons:
            button.clicked.connect(self._on_clear_click)

        # Structured Buttons
        self.search_struc_add.clicked.connect(self._on_add_click)
        self.search_struc_remove.clicked.connect(self._on_remove_click)

        # Reverse
        self.reverse_map.clicked.connect(self._on_point_click)

        # Batch
        self.batch_free.clicked.connect(lambda: processing.execAlgorithmDialog('{}:pelias_search_free'.format(PLUGIN_NAME)))
        self.batch_structured.clicked.connect(lambda: processing.execAlgorithmDialog('{}:pelias_search_structured'.format(PLUGIN_NAME)))
        self.batch_reverse.clicked.connect(lambda: processing.execAlgorithmDialog('{}:pelias_reverse'.format(PLUGIN_NAME)))

    def _on_reverse_select(self, tab_ind):
        """
        Hide GUI components which are not necessary for reverse.

        :param tab_ind: old index of main tab widget
        :type tab_ind: int
        """

        set_widget_state = False if tab_ind == 2 else True

        self.search_focus_group.setEnabled(set_widget_state)
        self.search_rest_rect_group.setEnabled(set_widget_state)
        self.search_rest_circle_group.setEnabled(set_widget_state)

    def _on_prov_refresh_click(self):
        """Populates provider dropdown with fresh list from config.yml"""

        providers = configmanager.read_config()['providers']
        self.provider_combo.clear()
        for provider in providers:
            self.provider_combo.addItem(provider['name'], provider)

    def _on_clear_click(self):
        """Clear the QgsFilterLineEdit widgets associated with the clear button"""

        sending_button = self.sender()
        parent_widget = sending_button.parentWidget()
        line_edit_widgets = parent_widget.findChildren(QgsFilterLineEdit)
        for widget in line_edit_widgets:
            widget.clearValue()


    def _on_remove_click(self):
        """remove layer: text from list box"""

        items = self.layer_list.selectedItems()
        for item in items:
            row = self.layer_list.row(item)
            self.layer_list.takeItem(row)

    def _on_add_click(self):
        """Add layer: text to list box"""

        current_text = self.search_struc_layers_text.value()
        current_layer = self.search_struc_layers_combo.currentText()

        if current_text != '':
            self.layer_list.addItem("=".join([current_layer, current_text]))

    def _on_rect_click(self):
        """Initialize the Rect map tool to select rectangle in map canvas."""

        # self.showMinimized()
        self.hide()
        self.rect_tool = maptools.RectTool(self.iface.mapCanvas())
        self.iface.mapCanvas().setMapTool(self.rect_tool)
        self.rect_tool.updateLabels.connect(self._writeRectLabel)

    def _writeRectLabel(self, rectangle):
        """
        Callback to write the line_tool rectangle to appropriate LineEdit widgets.

        :param rectangle: user drawn rectangle
        :type rectangle: QgsRectangle
        """
        self.search_rest_rect_xmin.setValue("{0:.6f}".format(rectangle.xMinimum()))
        self.search_rest_rect_ymin.setValue("{0:.6f}".format(rectangle.yMinimum()))
        self.search_rest_rect_xmax.setValue("{0:.6f}".format(rectangle.xMaximum()))
        self.search_rest_rect_ymax.setValue("{0:.6f}".format(rectangle.yMaximum()))

        self.rect_tool.updateLabels.disconnect()
        self.iface.mapCanvas().setMapTool(self.last_maptool)
        self.show()

    def _on_point_click(self):
        """Initialize the Point map tool to select coordinates in map canvas."""

        self.hide()
        sending_button = self.sender().objectName()
        self.point_tool = maptools.PointTool(self.iface.mapCanvas(), sending_button, 'icon_locate.png')
        self.iface.mapCanvas().setMapTool(self.point_tool)
        self.point_tool.canvasClicked.connect(self._writePointLabel)

    # Write map coordinates to text fields
    def _writePointLabel(self, point, button):
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
            # TODO: Add circle to map canvas
            # self._add_search_circle(point, radius)

        if button == self.reverse_map.objectName():
            self.reverse_x.setText("{0:.6f}".format(x))
            self.reverse_y.setText("{0:.6f}".format(y))

        # Restore old behavior
        QApplication.restoreOverrideCursor()
        self.point_tool.canvasClicked.disconnect()
        self.iface.mapCanvas().setMapTool(self.last_maptool)
        self.show()