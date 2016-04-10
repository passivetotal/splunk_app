import datetime
import splunk.Intersplunk
import traceback

from passivetotal.libs.dns import DnsRequest
from utilities import build_headers
from utilities import get_config
from utilities import setup_logging

logger = setup_logging()


try:
    logger.info("Starting command processing")
    input_events, dummyresults, settings = splunk.Intersplunk.getOrganizedResults()
    keywords, options = splunk.Intersplunk.getKeywordsAndOptions()

    kwords = {}
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

    logger.info("Query target: %s" % query_value)
    logger.debug("Raw options: %s" % str(options))

    configuration = get_config("passivetotal", "api-setup")
    username = configuration.get('username', None)
    api_key = configuration.get('apikey', None)

    output_events = list()
    pdns = DnsRequest(username, api_key, headers=build_headers()).get_unique_resolutions(**kwords)
    if 'error' in pdns:
        raise Exception("Whoa there, looks like you reached your quota for today! Please come back tomorrow to resume your investigation or contact support for details on enterprise plans.")
    for result in pdns.get("frequency", []):
        tmp = {'resolve': result[0], 'count': result[1]}
        output_events.append(tmp)
    splunk.Intersplunk.outputResults(output_events)

except Exception, e:
    stack = traceback.format_exc()
    splunk.Intersplunk.generateErrorResults(str(e))
    logger.error(str(e) + ". Traceback: " + str(stack))
