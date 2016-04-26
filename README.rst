PassiveTotal for Splunk
=======================

PassiveTotal for Splunk brings the power of datasets collected from Internet scanning directly to your Splunk instance. This application leverages your existing PassiveTotal account and our API in order to bring in data like passive DNS, WHOIS, passive SSL, host attributes and more.

Requirements
------------

Users will need a PassiveTotal account before being able to use the PassiveTotal Splunk app. Users can register for a free PassiveTotal account by visiting the following: https://www.passivetotal.org/register. Once approved, users will need to take note of their username (email used for sign-up) and the API key issued and found within the settings page.

Dependencies
------------

PassiveTotal for Splunk relies on passivetotal_ and requests_ for processing. Both libraries are bundled within the application and do not need to be installed manually on the system.

.. _passivetotal: https://pypi.python.org/pypi/passivetotal
.. _requests: http://docs.python-requests.org/en/master/

Installation
------------

PassiveTotal for Splunk can be installed in two ways, manual or automatically through splunkbase. The preferred method of installation is to use the Splunk portal which handles all installation details. If installing manually, see below:

1. Download the PassiveTotal app from Splunkbase_
2. Copy the output files to your Splunk server and install::

    splunk install app <passivetotal_splunk_app.tar.gz>

3. Restart Splunk and check out your apps
4. Associate your username and API key to complete the PassiveTotal setup

.. _Splunkbase: https://splunkbase.splunk.com/

*Note: Dependencies have been packaged inside of the app, but can be installed using the following*

    $SPLUNK_HOME/lib/python2.7/site-packages passivetotal

Features
--------

- Users can search for domains or IP addresses for more context
- Contextual data includes: passive DNS, WHOIS, passive SSL, host attributes, tags, classifications, unique resolutions
- Local events are automatically searched and referenced
- Pivots on returned data can be done both inside of Splunk or inside of PassiveTotal
- Users can access their team's search history directly from the dashboard

Available Commands
------------------

The following commands can be used outside the context of the PassiveTotal app in order to populate the "statistics" tab on search results:

- **ptenrich_command.py**: Perform enrichment on the supplied "query" to get tags, metadata and user classifications
- **pthistory_command.py**: Get the historic searches associated with the API key organization (*requires PassiveTotal enterprise*)
- **ptpdns_command.py**: Get the passive DNS information associated with the supplied "query" value
- **ptssl_command.py**: Get the passive SSL information associated with the supplied "query" value
- **pttrackers_command.py**: Get the tracking code information associated with the supplied "query" value
- **ptupdns_command.py**: Get the unique resolutions based on passive DNS associated with the supplied "query" value
- **ptwhois_command.py**: Get the WHOIS information associated with the supplied "query" value

Support
-------

To troubleshoot any commands invoked manually or automatically, add the following to your log.cfg file::

    splunk.passivetotal = DEBUG

Send any support related questions to feedback@passivetotal.org



