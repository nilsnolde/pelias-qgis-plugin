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

from datetime import datetime, timedelta
import requests
import time
import collections
from urllib.parse import urlencode

from PyQt5.QtCore import pyqtSignal, QObject

from PeliasGeocoding import __version__
from PeliasGeocoding.utils import logger, exceptions

_USER_AGENT = "PeliasQGISClient@v{}".format(__version__)


class Client(QObject):
    """Performs requests to Pelias API services."""

    def __init__(self,
                 provider,
                 retry_timeout=60):
        """
        Performs requests to Pelias API services.

        :param provider: A openrouteservice provider from config.yml
        :type provider: dict

        :param retry_timeout: Timeout across multiple retriable requests, in
            seconds.
        :type retry_timeout: int
        """
        QObject.__init__(self)

        self.key = provider['key']
        self.base_url = provider['base_url']
        self.limit = provider['limit']
        self.limit_unit = provider['unit']
        
        self.session = requests.Session()

        self.retry_timeout = timedelta(seconds=retry_timeout)
        self.requests_kwargs = dict()
        self.requests_kwargs.update({
            "headers": {"User-Agent": _USER_AGENT,
                        'Content-type': 'application/json'}
        })

        self.sent_times = collections.deque("", self.limit)

        # Save some references to retrieve in client instances
        self.url = None
        self.warnings = None

    overQueryLimit = pyqtSignal("int")
    def request(self, 
                url, params,
                first_request_time=None,
                requests_kwargs=None,
                post_json=None):
        """Performs HTTP GET/POST with credentials, returning the body asdlg
        JSON.

        :param url: URL extension for request. Should begin with a slash.
        :type url: string

        :param params: HTTP GET parameters.
        :type params: dict or list of key/value tuples

        :param first_request_time: The time of the first request (None if no
            retries have occurred).
        :type first_request_time: datetime.datetime

        :param requests_kwargs: Same extra keywords arg for requests as per
            __init__, but provided here to allow overriding internally on a
            per-request basis.
        :type requests_kwargs: dict

        :param post_json: Parameters for POST endpoints
        :type post_json: dict

        :raises PeliasGeocoding.utils.exceptions.ApiError: when the API returns an error.

        :returns: openrouteservice response body
        :rtype: dict
        """

        if not first_request_time:
            first_request_time = datetime.now()

        elapsed = datetime.now() - first_request_time
        if elapsed > self.retry_timeout:
            raise exceptions.Timeout()

        authed_url = self._generate_auth_url(url,
                                             params,
                                             )
        self.url = self.base_url + authed_url
        # Default to the client-level self.requests_kwargs, with method-level
        # requests_kwargs arg overriding.
        requests_kwargs = requests_kwargs or {}
        final_requests_kwargs = dict(self.requests_kwargs, **requests_kwargs)
        
        # Determine GET/POST
        requests_method = self.session.get
        # Keep for future compatibility of POST
        if post_json is not None:
            requests_method = self.session.post
            final_requests_kwargs["json"] = post_json

        logger.log(
            "url: {}\nParameters: {}".format(
                self.url,
                final_requests_kwargs
            ),
            0
        )

        try:
            response = requests_method(
                self.base_url + authed_url,
                **final_requests_kwargs
            )
        except requests.exceptions.Timeout:
            raise

        try:
            result = self._get_body(response)
            self.sent_times.append(time.time())

        except exceptions.OverQueryLimit as e:
            elapsed_since_earliest = time.time() - self.sent_times[0]
            interval = 60 if self.limit_unit == 'minute' else 1
            sleep_for = interval - elapsed_since_earliest

            # let the client know smth happened
            self.overQuerylimit.emit(sleep_for)
            logger.log("{}: {}".format(e.__class__.__name__, str(e)), 1)

            time.sleep(sleep_for)

            return self.request(url, params, first_request_time, requests_kwargs, post_json)

        except Exception as e:
            logger.log("{}: {}".format(e.__class__.__name__, str(e)), 2)
            raise

        # Write warnings
        self.warnings = result['geocoding'].get('warnings')

        return result


    @staticmethod
    def _get_body(response):
        """
        Casts JSON response to dict
        
        :param response: The HTTP response of the request.
        :type response: JSON object

        :raises PeliasGeocoding.utils.exceptions.OverQueryLimitError: when rate limit is exhausted, HTTP 429
        :raises PeliasGeocoding.utils.exceptions.ApiError: when the backend API throws an error, HTTP 400
        :raises PeliasGeocoding.utils.exceptions.InvalidKey: when API key is invalid (or quota is exceeded), HTTP 403
        :raises PeliasGeocoding.utils.exceptions.GenericServerError: all other HTTP errors

        :returns: response body
        :rtype: dict
        """
        body = response.json()
        status_code = response.status_code
        
        if status_code == 429:
            raise exceptions.OverQueryLimit(
                str(status_code),
                "\n".join(body['geocoding']['errors'])
            )
        # Internal error message for Bad Request
        if status_code == 400:
            raise exceptions.ApiError(
                str(status_code),
                "\n".join(body['geocoding']['errors'])
            )

        if status_code == 403:
            raise exceptions.InvalidKey(
                str(status_code),
                "Invalid key specified or quota exceeded."
            )
        # Other HTTP errors have different formatting
        if status_code != 200:
            raise exceptions.GenericServerError(
                status_code,
                body
            )

        return body

    def _generate_auth_url(self, path, params):
        """Returns the path and query string portion of the request URL, first
        adding any necessary parameters.

        :param path: The path portion of the URL.
        :type path: string

        :param params: URL parameters.
        :type params: dict or list of key/value tuples

        :returns: encoded URL
        :rtype: string
        """
        
        if type(params) is dict:
            params = sorted(dict(**params).items())
        
        # Only auto-add API key when using ORS. If own instance, API key must
        # be explicitly added to params
        if self.key != '':
            params.append(("api_key", self.key))

        return path + "?" + requests.utils.unquote_unreserved(urlencode(params))