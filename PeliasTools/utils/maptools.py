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

import os.path

from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QCursor, QPixmap, QColor
from PyQt5.QtWidgets import QApplication

from qgis.core import (QgsCoordinateReferenceSystem,
                       QgsCoordinateTransform,
                       QgsProject,
                       QgsWkbTypes,
                       QgsPointXY,
                       QgsRectangle,
                       Qgis)
from qgis.gui import QgsMapToolEmitPoint, QgsRubberBand

from PeliasTools import ICON_DIR, DEFAULT_COLOR


class PointTool(QgsMapToolEmitPoint):
    def __init__(self, canvas, button):
        QgsMapToolEmitPoint.__init__(self, canvas)
        self.canvas = canvas
        self.button = button
        self.cursor = QCursor(QPixmap(os.path.join(ICON_DIR, 'icon_locate.png')).scaledToWidth(48), 24, 24)
    
    canvasClicked = pyqtSignal(['QgsPointXY', 'QString'])
    def canvasReleaseEvent(self, event):
        #Get the click and emit a transformed point

        crsSrc = self.canvas.mapSettings().destinationCrs()
            
        crsWGS = QgsCoordinateReferenceSystem(4326)
    
        point_oldcrs = event.mapPoint()
        
        xform = QgsCoordinateTransform(crsSrc, crsWGS, QgsProject.instance())
        point_newcrs = xform.transform(point_oldcrs)
        
        QApplication.restoreOverrideCursor()
        
        self.canvasClicked.emit(point_newcrs, self.button)

    def activate(self):
        QApplication.setOverrideCursor(self.cursor)


class RectTool(QgsMapToolEmitPoint):
    def __init__(self, canvas):
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)

        self.rubberBand = QgsRubberBand(self.canvas, True)
        # self.rubberBand.setFillColor(QColor(DEFAULT_COLOR))
        self.rubberBand.setStrokeColor(QColor(DEFAULT_COLOR))
        self.rubberBand.setWidth(2)
        self.reset()

    def reset(self):
        self.startPoint = self.endPoint = None
        self.isEmittingPoint = False
        self.rubberBand.reset(True)

    def canvasPressEvent(self, e):
        self.startPoint = self.toMapCoordinates(e.pos())
        self.endPoint = self.startPoint
        self.isEmittingPoint = True
        self.showRect(self.startPoint, self.endPoint)

    updateLabels = pyqtSignal("QgsRectangle")
    def canvasReleaseEvent(self, e):
        self.isEmittingPoint = False
        r = self.rectangle()
        if r is not None:
            self.updateLabels.emit(r)
            self.rubberBand.hide()
            del self.rubberBand

    def canvasMoveEvent(self, e):
        if not self.isEmittingPoint:
            return

        self.endPoint = self.toMapCoordinates(e.pos())
        self.showRect(self.startPoint, self.endPoint)

    def showRect(self, startPoint, endPoint):
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
        if self.startPoint is None or self.endPoint is None:
            return None
        elif self.startPoint.x() == self.endPoint.x() or self.startPoint.y() == self.endPoint.y():
            return None

        return QgsRectangle(self.startPoint, self.endPoint)

    def deactivate(self):
        super(RectTool, self).deactivate()
        self.deactivated.emit()