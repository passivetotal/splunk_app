#!/usr/bin/env python
"""PassiveTotal API Interface."""

__author__ = 'Brandon Dixon (PassiveTotal)'
__version__ = '1.0.0'

import datetime
# custom
from passivetotal.api import Client
from passivetotal.response import Response
# exceptions
from passivetotal.common.exceptions import MISSING_FIELD
from passivetotal.common.exceptions import INVALID_FIELD_TYPE
# const
from passivetotal.common.const import WHOIS_VALID_FIELDS
from passivetotal.common.const import WHOIS_SECTIONS
from passivetotal.common.const import WHOIS_SECTION_FIELDS


class WhoisRequest(Client):

    """Client to interface with the WHOIS calls from the PassiveTotal API."""

    def __init__(self, *args, **kwargs):
        """Inherit from the base class."""
        super(WhoisRequest, self).__init__(*args, **kwargs)

    def get_whois_details(self, **kwargs):
        """Get WHOIS details based on query value.

        Reference:

        :param str query: Query value to use when making the request for data
        :param str compact_record: Return the record in a compact format
        :return: WHOIS details for the query
        """
        return self._get('whois', '', **kwargs)

    def search_whois_by_field(self, **kwargs):
        """Search WHOIS details based on query value and field.

        Reference:

        :param str query: Query value to use when making the request for data
        :param str compact_record: Return the record in a compact format
        :param str field: Field to run the query against
        :return: WHOIS records matching the query
        """
        if 'field' not in kwargs:
            raise MISSING_FIELD("Field value is required.")
        if kwargs['field'] not in WHOIS_VALID_FIELDS:
            raise INVALID_FIELD_TYPE("Field must be one of the following: %s"
                                     % ', '.join(WHOIS_VALID_FIELDS))
        return self._get('whois', 'search', **kwargs)


class WhoisResponse(Response):

    """Result object to ease interaction with data."""

    def __init__(self, *args, **kwargs):
        """Inherit from the base class."""
        super(WhoisResponse, self).__init__(*args, **kwargs)

    def get_days_since_registration(self):
        """Get the amount of days since WHOIS was registered.

        :return: Number of days since WHOIS registration
        """
        tmp = self._load_time(self.registryUpdatedAt, "%Y-%m-%d")
        current_time = datetime.datetime.now()
        return (current_time - tmp).days

    def get_days_since_updated(self):
        """Get the amount of days since WHOIS was updated.

        :return: Number of days since WHOIS update
        """
        tmp = self._load_time(self.registered, "%Y-%m-%d")
        current_time = datetime.datetime.now()
        return (current_time - tmp).days

    def get_days_until_expiration(self):
        """Get the amount of days until the WHOIS expires.

        :return: Number of days since WHOIS expires
        """
        tmp = self._load_time(self.expiresAt, "%Y-%m-%d")
        current_time = datetime.datetime.now()
        return (current_time - tmp).days

    @property
    def text(self):
        """Output data as text.

        Data shown in the text output is not full-featured and contains only
        content deemed to be most useful to the end-user. For full data output,
        use JSON or XML outputs.

        :return: String of formatted data
        """
        output = ''
        output += "[*] Domain: %s\n" % self.domain
        output += "[*] Created: %s\n" % self.registered
        output += "[*] Updated: %s\n" % self.registryUpdatedAt
        output += "[*] Expires: %s\n" % self.expiresAt
        output += "[*] Registrar: %s\n" % self.registrar
        output += "[*] Server: %s\n" % self.whoisServer
        output += "[*] Nameservers: %s\n" % ', '.join(self.nameServers)
        output += "[*] Contact Email: %s\n" % self.contactEmail
        output += "[*] Sections:\n"
        for section in WHOIS_SECTIONS:
            data = self._results.get(section, {})
            output += "=> %s\n" % section.title()
            for header in WHOIS_SECTION_FIELDS[1:]:
                output += "\t%s: %s\n" % (
                    header.title(),
                    data.get(header, '')
                )

        return output


class WhoisSearchResponse(object):

    """Process records from search response."""

    def __init__(self, results):
        """Load all the records into WHOIS responses."""
        self._results = results
        self._records = list()
        for item in self._results.get('results', []):
            self._records.append(WhoisResponse(item))

    def get_records(self):
        return self._records

    @property
    def records(self):
        return self._records
