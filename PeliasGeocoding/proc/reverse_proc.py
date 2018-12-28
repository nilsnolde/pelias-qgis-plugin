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

from PyQt5.QtGui import QIcon

from qgis.core import (QgsWkbTypes,
                       QgsCoordinateReferenceSystem,
                       QgsProcessing,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterField,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterString,
                       QgsProcessingParameterEnum,
                       QgsProcessingParameterNumber,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterPoint,
                       QgsProcessingParameterExtent)

from . import HELP_DIR
from PeliasGeocoding import RESOURCE_PREFIX, __help__
from PeliasGeocoding.core import client, LAYERS, SOURCES, response_handler
from PeliasGeocoding.utils import exceptions, configmanager, logger, convert, transform


class PeliasReverseAlgo(QgsProcessingAlgorithm):
    # TODO: create base algorithm class common to all modules

    ALGO_NAME = 'pelias_reverse'
    ALGO_NAME_LIST = ALGO_NAME.split("_")

    IN_PROVIDER = "INPUT_PROVIDER"
    IN_POINTS = "INPUT_POINT_LAYER"
    IN_ID_FIELD = "INPUT_ID_FIELD"
    IN_COUNTRY = 'INPUT_COUNTRY'
    IN_LAYERS = 'INPUT_LAYERS'
    IN_SOURCES = 'INPUT_SOURCES'
    IN_SIZE = 'INPUT_SIZE'
    OUT = 'OUTPUT'

    # Save some important references
    crs_out = QgsCoordinateReferenceSystem(4326)
    providers = configmanager.read_config()['providers']
    # difference = None

    def initAlgorithm(self, configuration, p_str=None, Any=None, *args, **kwargs):

        providers = [provider['name'] for provider in self.providers]

        self.addParameter(
            QgsProcessingParameterEnum(
                self.IN_PROVIDER,
                "Provider",
                providers
            )
        )

        self.addParameter(
            QgsProcessingParameterFeatureSource(
                name=self.IN_POINTS,
                description="Input Point layer",
                types=[QgsProcessing.TypeVectorPoint],
            )
        )

        self.addParameter(
            QgsProcessingParameterField(
                name=self.IN_ID_FIELD,
                description="Input layer ID Field",
                parentLayerParameterName=self.IN_POINTS
            )
        )

        self.addParameter(
            QgsProcessingParameterString(
                name=self.IN_COUNTRY,
                description="Restrict search to country",
                optional=True,
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                name=self.IN_LAYERS,
                description="Filter by administrative type",
                optional=True,
                options=LAYERS,
                allowMultiple=True
            )
        )

        self.addParameter(
            QgsProcessingParameterEnum(
                name=self.IN_SOURCES,
                description="Filter by data source",
                optional=True,
                options=SOURCES,
                allowMultiple=True
            )
        )

        self.addParameter((
            QgsProcessingParameterNumber(
                name=self.IN_SIZE,
                description="Limit to number of features",
                defaultValue=5,
                minValue=1,
                maxValue=40
            )
        ))

        self.addParameter(
            QgsProcessingParameterFeatureSink(
                name=self.OUT,
                description="Pelias Reverse Geocoding",
                createByDefault=False
            )
        )

    def name(self):
        return self.ALGO_NAME

    def shortHelpString(self):
        """Displays the sidebar help in the algorithm window"""

        file = os.path.join(
            HELP_DIR,
            'algorithm_freetext.help'
        )
        with open(file) as helpf:
            msg = helpf.read()

        return msg

    def helpUrl(self):
        """will be connected to the Help button in the Algorithm window"""
        return __help__

    def displayName(self):
        return " ".join(map(lambda x: x.capitalize(), self.ALGO_NAME_LIST))

    def icon(self):
        return QIcon(RESOURCE_PREFIX + 'icon_locate.png')

    def createInstance(self):
        return PeliasReverseAlgo()

    def processAlgorithm(self, parameters, context, feedback):
        # Init client
        provider = self.providers[self.parameterAsEnum(parameters, self.IN_PROVIDER, context)]
        in_source = self.parameterAsSource(parameters, self.IN_POINTS, context)
        in_id_field_name = self.parameterAsString(parameters, self.IN_ID_FIELD, context)
        in_country = self.parameterAsString(parameters, self.IN_COUNTRY, context)
        in_layers = self.parameterAsEnums(parameters, self.IN_LAYERS, context)
        in_sources = self.parameterAsEnums(parameters, self.IN_SOURCES, context)
        in_size = self.parameterAsInt(parameters, self.IN_SIZE, context)

        # Get user specified ID field as object
        in_id_field = in_source.fields().field(in_id_field_name)

        clnt = client.Client(provider)
        clnt.overQueryLimit.connect(lambda sleep_for: feedback.reportError("OverQueryLimit: Wait for {} seconds".format(sleep_for)))

        params = dict()

        if in_country:
            params['boundary.country'] = in_country
        if in_layers:
            params['layers'] = convert.comma_list([LAYERS[idx] for idx in in_layers])
        if in_sources:
            params['sources'] = convert.comma_list([SOURCES[idx] for idx in in_sources])
        params['size'] = str(in_size)

        responsehandler = response_handler.ResponseHandler(in_id_field)

        (sink, dest_id) = self.parameterAsSink(parameters, self.OUT, context,
                                               responsehandler.get_fields(),
                                               QgsWkbTypes.Point,
                                               self.crs_out)

        xformer = transform.transformToWGS(in_source.sourceCrs())
        for num, feat_in in enumerate(in_source.getFeatures()):
            x_point = xformer.transform(feat_in.geometry().asPoint())
            params['point.lon'] = x_point.x()
            params['point.lat'] = x_point.y()

            in_id_field_value = feat_in[in_id_field_name]
            try:
                response = clnt.request(provider['endpoints'][self.ALGO_NAME_LIST[1]],
                                        params)
            except (exceptions.ApiError,
                    exceptions.GenericServerError,
                    exceptions.InvalidKey) as e:
                msg = "Feature ID {} caused a {}:\n{}".format(
                    in_id_field_value,
                    e.__class__.__name__,
                    str(e))
                feedback.reportError(msg)
                logger.log(msg, 2)
                continue

            features_out = responsehandler.generate_out_features(response, in_id_field_value)
            for feat_out in features_out:
                sink.addFeature(feat_out)

            feedback.setProgress(int(100.0 / in_source.featureCount() * num))

        return {self.OUT: dest_id}
