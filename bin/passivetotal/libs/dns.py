#!/usr/bin/env python
"""PassiveTotal API Interface."""

__author__ = 'Brandon Dixon (PassiveTotal)'
__version__ = '1.0.0'

import datetime
# custom
from passivetotal.api import Client
from passivetotal.response import Response
# exceptions
from passivetotal.common.exceptions import INVALID_VALUE_TYPE


class DnsRequest(Client):

    """Client to interface with the DNS calls from the PassiveTotal API."""

    def __init__(self, *args, **kwargs):
        """Inherit from the base class."""
        super(DnsRequest, self).__init__(*args, **kwargs)

    def get_passive_dns(self, **kwargs):
        """Get passive DNS data based on a query value.

        Reference: https://api.passivetotal.org/api/docs/#api-DNS-GetDnsPassiveQuery

        :param str query: Query value to use when making the request for data
        :param str start: Starting period for record filtering
        :param str end: Ending period for record filtering
        :param int timeout: Timeout to apply to source queries
        :param list sources: List of sources to use for the query
        :return: List of passive DNS results
        """
        return self._get('dns', 'passive', **kwargs)

    def get_unique_resolutions(self, **kwargs):
        """Get unique resolutions from passive DNS.

        Reference: https://api.passivetotal.org/api/docs/#api-DNS-GetDnsPassiveUniqueQuery

        :param str query: Query value to use when making the request for data
        :param str start: Starting period for record filtering
        :param str end: Ending period for record filtering
        :param int timeout: Timeout to apply to source queries
        :param list sources: List of sources to use for the query
        :return: List of passive DNS unique resolutions
        """
        return self._get('dns', 'passive', 'unique', **kwargs)


class DnsRecord(object):

    """Provide some basic helpers for the DNS records."""

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

    def _load_time(self, time_period):
        """Convert a str date to true datetime.

        :param str time_period: Date period of the record
        :return: Loaded datetime object from the string
        """
        return datetime.datetime.strptime(
            time_period, "%Y-%m-%d %H:%M:%S"
        )

    def get_observed_days(self):
        """Get the amount of days observed for the record period.

        :return: Number of days observed
        """
        first_seen = self._load_time(self.firstSeen)
        last_seen = self._load_time(self.lastSeen)
        return (last_seen - first_seen).days

    def get_days_until_now(self):
        """Get the amount of days from last seen until today.

        :return: Number of days until now
        """
        last_seen = self._load_time(self.lastSeen)
        current_time = datetime.datetime.now()
        return (current_time - last_seen).days

    def get_source_count(self):
        """Get the number of sources used to create the record.

        :return: Number of sources used for the record
        """
        return len(self.sources)


class DnsResponse(Response):

    """Result object to ease interaction with data."""

    def __init__(self, *args, **kwargs):
        """Inherit from the base class."""
        super(DnsResponse, self).__init__(*args, **kwargs)
        self._process_records()

    def _process_records(self):
        """Process the passive DNS data."""
        self._records = list()
        for record in self.results:
            wrapped = DnsRecord.process(record)
            self._records.append(wrapped)

    def get_records(self):
        """Get the DNS records."""
        return self._records

    def get_observed_days(self):
        """Get the amount of days observed for the query period.

        :return: Nunber of observed days
        """
        first_seen = self._load_time(self.firstSeen, "%Y-%m-%d %H:%M:%S")
        last_seen = self._load_time(self.lastSeen, "%Y-%m-%d %H:%M:%S")
        return (last_seen - first_seen).days

    def get_days_until_now(self):
        """Get the amount of days from last seen until today.

        :return: Nunber of days until now
        """
        last_seen = self._load_time(self.lastSeen, "%Y-%m-%d %H:%M:%S")
        current_time = datetime.datetime.now()
        return (current_time - last_seen).days

    def get_source_variety(self):
        """Get the contribution count for each source for the results.

        :return: Dict of sources and their counts based on data
        """
        sources = dict()
        for item in self._records:
            for source in item.source:
                if source in sources:
                    sources[source] += 1
                else:
                    sources[source] = 1

        return sources


class UniqueDnsRecord(object):

    """Provide some basic helpers for the DNS unique records."""

    def __init__(self, record):
        """Initialize the class.

        :param list results: Record to load into the class
        """
        if type(record) != list:
            raise INVALID_VALUE_TYPE("Record must be of type list")
        self._record = record
        self.resolve, self.count = record

    @classmethod
    def process(inferred, record):
        """Process results and return a loaded instance.

        :param object inferred: Instance of the class itself
        :param dict record: Record to use for loading
        :return: Instance of the loaded class
        """
        return inferred(record)


class DnsUniqueResponse(Response):

    """Result object to ease interaction with data."""

    def __init__(self, *args, **kwargs):
        """Inherit from the base class."""
        super(DnsUniqueResponse, self).__init__(*args, **kwargs)

        self._records = list()
        self._process_records()

    def _process_records(self):
        """Process the passive DNS data."""
        self._records = list()
        for record in self.frequncy:
            wrapped = UniqueDnsRecord.process(record)
            self._records.append(wrapped)

    def get_records(self):
        """Get a list of unique resolution records."""
        return self._records
