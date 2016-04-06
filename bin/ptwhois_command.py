import splunk.Intersplunk
import traceback

from passivetotal.libs.whois import WhoisRequest
from utilities import build_headers
from utilities import gen_label
from utilities import get_config
from utilities import setup_logging

logger = setup_logging()


try:
    logger.info("Starting command processing")
    input_events, dummyresults, settings = splunk.Intersplunk.getOrganizedResults()
    keywords, options = splunk.Intersplunk.getKeywordsAndOptions()

    query_value = options.get("query", "")
    logger.info("Query target: %s" % query_value)
    logger.debug("Raw options: %s" % str(options))

    configuration = get_config("passivetotal", "api-setup")
    username = configuration.get('username', None)
    api_key = configuration.get('apikey', None)

    output_events = list()
    whois = WhoisRequest(username, api_key).get_whois_details(
        query=query_value, compact_record=True, headers=build_headers())
    if 'error' in whois:
        raise Exception("Whoa there, looks like you reached your quota for today! Please come back tomorrow to resume your investigation or contact support for details on enterprise plans.")
    fields = ['contactEmail', 'nameServers', 'registered', 'registryUpdatedAt',
              'expiresAt', 'registrar']
    for field in fields:
        tmp = {'key': gen_label(field), 'value': whois.get(field, '')}
        output_events.append(tmp)
    for key, value in whois.get('compact', {}).iteritems():
        formatted = list()
        for item in value.get('values', []):
            tmp = "%s (%s)" % (item[0], ', '.join(item[1]))
            formatted.append(tmp)
        tmp = {'key': gen_label(key), 'value': ', '.join(formatted)}
        output_events.append(tmp)
    splunk.Intersplunk.outputResults(output_events)

except Exception, e:
    stack = traceback.format_exc()
    splunk.Intersplunk.generateErrorResults(str(e))
    logger.error(str(e) + ". Traceback: " + str(stack))