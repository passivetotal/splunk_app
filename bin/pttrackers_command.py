import splunk.Intersplunk
import traceback

from passivetotal.libs.attributes import AttributeRequest
from utilities import build_headers
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

    output_events = []
    tmp = AttributeRequest(username, api_key, headers=build_headers()).get_host_attribute_trackers(
        query=query_value)
    if 'error' in tmp:
        raise Exception("Whoa there, looks like you reached your quota for today! Please come back tomorrow to resume your investigation or contact support for details on enterprise plans.")
    for result in tmp.get("results", []):
        output_events.append(result)
    splunk.Intersplunk.outputResults(output_events)

except Exception, e:
    stack = traceback.format_exc()
    splunk.Intersplunk.generateErrorResults(str(e))
    logger.error(str(e) + ". Traceback: " + str(stack))
