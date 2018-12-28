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

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QCursor, QPixmap, QColor
from PyQt5.QtWidgets import QApplication

from qgis.core import (QgsWkbTypes,
                       QgsPointXY,
                       QgsRectangle)
from qgis.gui import QgsMapToolEmitPoint, QgsRubberBand

from PeliasGeocoding import DEFAULT_COLOR, RESOURCE_PREFIX
from .transform import transformToWGS


class PointTool(QgsMapToolEmitPoint):
    """Point Map tool to capture mapped coordinates."""

    def __init__(self, canvas, button='None', icon=None):
        """
        :param canvas: current map canvas
        :type: QgsMapCanvas

        :param button: name of 'Map!' button pressed.
        :type button: str
        """

        QgsMapToolEmitPoint.__init__(self, canvas)
        self.canvas = canvas
        self.button = button
        # self.cursor = QCursor(QPixmap(os.path.join(ICON_DIR, 'icon_locate.png')).scaledToWidth(48), 24, 24)
        self.cursor = QCursor(QPixmap(RESOURCE_PREFIX + icon).scaledToWidth(48), 24, 24)

    canvasClicked = pyqtSignal(['QgsPointXY', 'QString'])
    def canvasReleaseEvent(self, event):
        #Get the click and emit a transformed point

        point_oldcrs = event.mapPoint()

        crsSrc = self.canvas.mapSettings().destinationCrs()
        xform = transformToWGS(crsSrc)
        point_newcrs = xform.transform(point_oldcrs)
        
        QApplication.restoreOverrideCursor()
        
        self.canvasClicked.emit(point_newcrs, self.button)

    def activate(self):
        QApplication.setOverrideCursor(self.cursor)


class RectTool(QgsMapToolEmitPoint):
    """Rectangle Map tool to capture mapped extent."""

    def __init__(self, canvas):
        """
        :param canvas: current map canvas
        :type canvas: QgsMapCanvas
        """

        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)

        self.rubberBand = QgsRubberBand(self.canvas, True)
        # self.rubberBand.setFillColor(QColor(DEFAULT_COLOR))
        self.rubberBand.setStrokeColor(QColor(DEFAULT_COLOR))
        self.rubberBand.setWidth(2)
        self.reset()

    def reset(self):
        """reset rubberband and captured points."""

        self.startPoint = self.endPoint = None
        self.isEmittingPoint = False
        self.rubberBand.reset(True)

    def canvasPressEvent(self, e):
        """Initialize rectangle drawing."""

        self.startPoint = self.toMapCoordinates(e.pos())
        self.endPoint = self.startPoint
        self.isEmittingPoint = True
        self.showRect(self.startPoint, self.endPoint)

    updateLabels = pyqtSignal("QgsRectangle")
    def canvasReleaseEvent(self, e):
        """Emits rectangle when button is released, delete rubberband."""

        self.isEmittingPoint = False
        r = self.rectangle()
        if r is not None:
            self.updateLabels.emit(r)
            self.rubberBand.hide()
            del self.rubberBand

    def canvasMoveEvent(self, e):
        """Draw rectangle"""
        if not self.isEmittingPoint:
            return

        self.endPoint = self.toMapCoordinates(e.pos())
        self.showRect(self.startPoint, self.endPoint)

    def showRect(self, startPoint, endPoint):
        """
        Build ruberband from two points.

        :param startPoint: first clicked point
        :type startPoint: QgsPointXY

        :param endPoint: Point at mouse release
        :type endPoint: QgsPointXY
        """
        self.rubberBand.reset(QgsWkbTypes.PolygonGeometry)
        if startPoint.x() == endPoint.x() or startPoint.y() == endPoint.y():
            return

        point1 = QgsPointXY(startPoint.x(), startPoint.y())
        point2 = QgsPointXY(startPoint.x(), endPoint.y())
        point3 = QgsPointXY(endPoint.x(), endPoint.y())
        point4 = QgsPointXY(endPoint.x(), startPoint.y())

        self.rubberBand.addPoint(point1, False)
        self.rubberBand.addPoint(point2, False)
        self.rubberBand.addPoint(point3, False)
        self.rubberBand.addPoint(point4, True)  # true to update canvas
        self.rubberBand.show()

    def rectangle(self):
        """Build rectangle to emit."""
        if self.startPoint is None or self.endPoint is None:
            return None
        elif self.startPoint.x() == self.endPoint.x() or self.startPoint.y() == self.endPoint.y():
            return None

        crsSrc = self.canvas.mapSettings().destinationCrs()
        xform = transformToWGS(crsSrc)
        startPoint_WGS = xform.transform(self.startPoint)
        endPoint_WGS = xform.transform(self.endPoint)

        return QgsRectangle(startPoint_WGS, endPoint_WGS)

    def deactivate(self):
        super(RectTool, self).deactivate()
        self.deactivated.emit()
