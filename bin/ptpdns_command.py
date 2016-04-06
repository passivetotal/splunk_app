import copy
import datetime
import splunk.Intersplunk
import traceback

from passivetotal.libs.dns import DnsRequest
from utilities import build_headers
from utilities import get_config
from utilities import setup_logging

logger = setup_logging()


def remove_keys(obj, keys=[]):
    """Remove a set of keys from a dict."""
    obj = copy.deepcopy(obj)
    for key in keys:
        obj.pop(key, None)
    return obj

try:
    logger.info("Starting command processing")
    input_events, dummyresults, settings = splunk.Intersplunk.getOrganizedResults()
    keywords, options = splunk.Intersplunk.getKeywordsAndOptions()

    kwords = dict()
    query_value = options.get("query", "")
    earliest = options.get("earliest", None)
    latest = options.get("latest", None)
    if earliest and earliest.isdigit():
        start = datetime.datetime.fromtimestamp(int(earliest))
        kwords['start'] = start.strftime("%Y-%m-%d")
    if latest and (latest.isdigit() or latest == 'now'):
        if latest == 'now':
            end = datetime.datetime.now()
        else:
            end = datetime.datetime.fromtimestamp(int(latest))
        kwords['end'] = end.strftime("%Y-%m-%d")
    kwords['query'] = query_value
    kwords['headers'] = build_headers()

    logger.info("Query target: %s" % query_value)
    logger.debug("Raw options: %s" % str(options))

    configuration = get_config("passivetotal", "api-setup")
    username = configuration.get('username', None)
    api_key = configuration.get('apikey', None)

    output_events = list()
    pdns = DnsRequest(username, api_key).get_passive_dns(**kwords)
    if 'error' in pdns:
        raise Exception("Whoa there, looks like you reached your quota for today! Please come back tomorrow to resume your investigation or contact support for details on enterprise plans.")
    for result in pdns.get("results", []):
        result = remove_keys(result, ['value', 'recordHash', 'collected'])
        result['count'] = pdns.get('totalRecords', 0)
        output_events.append(result)
    splunk.Intersplunk.outputResults(output_events)

except Exception, e:
    stack = traceback.format_exc()
    splunk.Intersplunk.generateErrorResults(str(e))
    logger.error(str(e) + ". Traceback: " + str(stack))