import splunk.Intersplunk
import traceback

from passivetotal.libs.actions import ActionsClient
from passivetotal.libs.enrichment import EnrichmentRequest
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

    output_events = list()
    enrichment = EnrichmentRequest(username, api_key).get_enrichment(
        query=query_value, headers=build_headers())
    if 'error' in enrichment:
        raise Exception("Whoa there, looks like you reached your quota for today! Please come back tomorrow to resume your investigation or contact support for details on enterprise plans.")
    classification = ActionsClient(username, api_key).get_classification_status(
        query=query_value, headers=build_headers())
    tmp = classification.get('classification', 'unknown').replace('_', '-')
    if tmp == '':
        tmp = 'unknown'
    enrichment['tags'].append(tmp)
    classification_lookup = {'non-malicious': 1, 'suspicious': 2,
                             'malicious': 3, 'unknown': 0, '': 0}
    enrichment['classification'] = classification_lookup[tmp]
    logger.info(enrichment)
    output_events.append(enrichment)
    splunk.Intersplunk.outputResults(output_events)

except Exception, e:
    stack = traceback.format_exc()
    splunk.Intersplunk.generateErrorResults(str(e))
    logger.error(str(e) + ". Traceback: " + str(stack))
