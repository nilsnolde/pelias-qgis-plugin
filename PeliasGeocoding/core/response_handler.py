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

from PyQt5.QtCore import QVariant

from qgis.core import QgsField, QgsFields, QgsFeature, QgsGeometry, QgsPointXY, QgsVectorLayer
from collections import OrderedDict


class ResponseHandler:
    """Populate Fields and features for response of API endpoints"""

    def __init__(self, id_field, debug=False):
        """
        :param id_field: ID field set by user.
        :type id_field: QgsField

        :param debug: Switch for debug mode, which will output all '_gid' response fields
        :type debug: boolean
        """
        self.id_field = id_field
        self.debug = debug

        self.fields_map = self._get_fields_mapping()
        self.fields = QgsFields()

    def generate_out_features(self, response, id_field_value):
        """
        Generator for output features from response.

        :param response: API response from a Pelias provider.
        :type response: dict

        :param id_field_value: Value of user set ID field
        :type id_field_value: any

        :returns: yields built feature to be inserted to output layer.
        :rtype: QgsFeature
        """

        for point in response['features']:
            feat = QgsFeature()
            coords = point['geometry']['coordinates']
            feat.attributes()
            feat.setGeometry(QgsGeometry().fromPointXY(QgsPointXY(*coords)))
            feat.setFields(self.fields)
            feat.setAttribute(self.id_field.name(), id_field_value)

            for attr in point['properties']:
                field_attr = self.fields_map.get(attr)
                if field_attr is not None:
                    feat.setAttribute(field_attr['nice_name'], point['properties'][attr])

            yield feat

    def get_layer(self, name, response):
        """
        Returns a populated Point layer to GUI control.

        :param name: Name for output layer
        :type name: str

        :param response: API response from Pelias provider.
        :type response: dict

        :returns: output Point layer
        :rtype: QgsVectorLayer
        """
        layer_out = QgsVectorLayer("Point?crs=EPSG:4326", 'Pelias ' + name.capitalize() + ' Geocoding', "memory")
        layer_out.dataProvider().addAttributes(self.get_fields())
        layer_out.updateFields()

        for feat in self.generate_out_features(response, None):
            layer_out.dataProvider().addFeature(feat)

        return layer_out

    def get_fields(self):
        """
        Builds fields() object for layer.

        :returns: initialized fields for layer
        :rtype: QgsFields
        """
        for field in self.fields_map.values():
            self.fields.append(QgsField(field['nice_name'], field['type']))

        return self.fields

    def _get_fields_mapping(self):
        """
        Map response fields to layer field proxies.

        :returns: fields map to retrieve field attributes later on.
        :rtype: OrderedDict
        """

        def _get_dict(nice_name, type=QVariant.String):
            return dict(type=type, nice_name=nice_name)

        id_field_name = self.id_field.name()
        id_field_type = self.id_field.type()
        fields_map = OrderedDict([
            (id_field_name, _get_dict(id_field_name, id_field_type)),
            ("name", _get_dict('nice_name')),
            ("label", _get_dict('label')),
            ("confidence", _get_dict('confidence', QVariant.Double)),
            ("accuracy", _get_dict('accuracy')),
            ("source", _get_dict('source')),
            ("layer", _get_dict('layer')),
            ("street", _get_dict('street')),
            ("housenumber", _get_dict('housenumber')),
            ("postalcode", _get_dict('postalcode')),
            ("locality", _get_dict('locality')),
            ("microhood", _get_dict('microhood')),
            ("neighborhood", _get_dict('neighbourhood')),
            ("borough", _get_dict('borough')),
            ("macrohood", _get_dict('macrohood')),
            ("localadmin", _get_dict('localadmin')),
            ("county", _get_dict('county')),
            ("macrocounty", _get_dict('macrocounty')),
            ("region", _get_dict('region')),
            ("macroregion", _get_dict('macroregion')),
            ("country", _get_dict('country')),
            ("empire", _get_dict('empire')),
            ("continent", _get_dict('continent')),
        ])

        if self.debug:
            fields_map.update(
                OrderedDict(
                    source_id=_get_dict('source_id'),
                    locality_gid=_get_dict('locality_id'),
                    microhood_gid=_get_dict('microhood_id'),
                    neighbourhood_gid=_get_dict('neighbourhood_id'),
                    borough_gid=_get_dict('borough_id'),
                    macrohood_gid=_get_dict('macrohood_id'),
                    localadmin_gid=_get_dict('localadmin_id'),
                    county_gid=_get_dict('county_id'),
                    macrocounty_gid=_get_dict('macrocounty_id'),
                    region_gid=_get_dict('region_id'),
                    macroregion_gid=_get_dict('macroregion_id'),
                    country_gid=_get_dict('country_id'),
                    empire_gid=_get_dict('empire_id'),
                    continent_gid=_get_dict('continent_id')
                )
            )

        return fields_map
