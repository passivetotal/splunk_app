import splunk.Intersplunk
import traceback

from passivetotal.libs.account import AccountClient
from utilities import build_headers
from utilities import get_config
from utilities import setup_logging

logger = setup_logging()


try:
    logger.info("Starting command processing")
    input_events, dummyresults, settings = splunk.Intersplunk.getOrganizedResults()
    keywords, options = splunk.Intersplunk.getKeywordsAndOptions()

    configuration = get_config("passivetotal", "api-setup")
    username = configuration.get('username', None)
    api_key = configuration.get('apikey', None)

    output_events = list()
    tmp = AccountClient(username, api_key, headers=build_headers()).get_account_organization_teamstream()
    for item in tmp.get('teamstream', []):
        if item['type'] != 'search':
            continue
        output_events.append(item)
    splunk.Intersplunk.outputResults(output_events)

except Exception, e:
    stack = traceback.format_exc()
    splunk.Intersplunk.generateErrorResults(str(e))
    logger.error(str(e) + ". Traceback: " + str(stack))