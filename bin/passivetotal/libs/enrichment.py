#!/usr/bin/env python
"""PassiveTotal API Interface."""

__author__ = 'Brandon Dixon (PassiveTotal)'
__version__ = '1.0.0'

from passivetotal.api import Client
from passivetotal.response import Response
# exceptions
from passivetotal.common.exceptions import INVALID_VALUE_TYPE


class EnrichmentRequest(Client):

    """Client to interface with the enrichment calls from the PassiveTotal API."""

    def __init__(self, *args, **kwargs):
        """Setup the primary client instance."""
        super(EnrichmentRequest, self).__init__(*args, **kwargs)

    def get_enrichment(self, **kwargs):
        """Get enrichment data for a value.

        Reference:

        :param query: Value to enrich
        :return: Dict of results
        """
        return self._get('enrichment', '', **kwargs)

    def get_osint(self, **kwargs):
        """Get OSINT data for a value.

        Reference:

        :param query: Value to search for in OSINT
        :return: Dict of results
        """
        return self._get('enrichment', 'osint', **kwargs)

    def get_malware(self, **kwargs):
        """Get malware data for a value.

        Reference:

        :param query: Value to search for in malware
        :return: Dict of results
        """
        return self._get('enrichment', 'malware', **kwargs)

    def get_subdomains(self, **kwargs):
        """Get listing of subdomains for a given query.

        Reference:
        """
        return self._get('enrichment', 'subdomains', **kwargs)


class GeneticRecord(object):
    def __init__(self, record):
        """Initialize the class.

        :param dict record: Record to load into the class
        """
        if type(record) != dict:
            raise INVALID_VALUE_TYPE("Record must be of type dict")
        self._record = record
        for key, value in self._record.iteritems():
            setattr(self, key, value)

    @classmethod
    def process(inferred, record):
        """Process results and return a loaded instance.

        :param object inferred: Instance of the class itself
        :param dict record: Record to use for loading
        :return: Instance of the loaded class
        """
        return inferred(record)


class GenericResponse(Response):

    """Result object to ease interaction with data."""

    def __init__(self, *args, **kwargs):
        """Inherit from the base class."""
        super(GenericResponse, self).__init__(*args, **kwargs)
        if 'results' in self._results:
            self._process_records()

    def _process_records(self):
        """Process the data."""
        self._records = list()
        for record in self.results:
            wrapped = GeneticRecord.process(record)
            self._records.append(wrapped)

    def get_records(self):
        """Get the loaded records."""
        return self._records
