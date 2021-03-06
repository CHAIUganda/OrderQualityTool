import pygogo
from bs4 import BeautifulSoup

from splinter import Browser

from dashboard.data.html_data_import import TR, TD
from dashboard.helpers import HTML_PARSER
from dynamic_preferences.registries import global_preferences_registry

from dashboard.utils import log_formatter, should_log_time

logger = pygogo.Gogo(__name__, low_formatter=log_formatter).get_logger()
logger.setLevel("INFO" if should_log_time() else "ERROR")


def get_html_table(html_doc, report_id):
    soup = BeautifulSoup(html_doc, HTML_PARSER)
    tables = soup.find_all("table")
    if len(tables) > 0:
        logger.debug(
            "found tables", extra={"count": len(tables), "report_id": report_id}
        )
        largest = tables[0]
        for table in filter(lambda t: t != largest, tables):
            rows = table.findChildren([TD, TR])
            rows_in_largest = largest.findChildren([TR, TD])
            if len(rows) > len(rows_in_largest):
                largest = table
        return largest
    logger.debug("No table found for %s", report_id)
    return None


class DHIS2Scrapper(object):

    def __init__(self):
        global_preferences = global_preferences_registry.manager()

        username = global_preferences.get("DHIS2_Settings__DHIS2_USERNAME")
        password = global_preferences.get("DHIS2_Settings__DHIS2_PASSWORD")
        base_url = global_preferences.get("DHIS2_Settings__DHIS2_URL")
        self.base_url = base_url

        browser = Browser("phantomjs")
        about_page_path = "dhis-web-commons-about/about.action"
        login_url = "%s/%s" % (base_url, about_page_path)
        logger.debug("login", extra={"url": login_url})

        browser.visit(login_url)
        self.browser = browser
        login_path = "dhis-web-commons/security/login.action"
        if login_path in browser.url:
            browser.fill(USERNAME_FIELD, username)
            browser.fill(PASSWORD_FIELD, password)
            button = browser.find_by_css("input.button")
            button.click()
            not_on_login_page = len(browser.find_by_css(".loginPage")) == 0
            if not_on_login_page:
                logger.debug(
                    "login success",
                    extra={
                        "login_url": login_url,
                        "username": username,
                        "browser_url": browser.url,
                    },
                )

            else:
                current_html = browser.html
                logger.debug(
                    "login failed",
                    extra={
                        "login_url": login_url,
                        "username": username,
                        "browser_url": browser.url,
                        "html": current_html,
                    },
                )
                raise Exception("dhis2 login failed")
        else:
            logger.debug("no login redirect", extra={"browser_url": browser.url})

    def get_standard_report(self, report_id, period, org_unit):
        query = {
            BASE_URL: self.base_url,
            REPORT_ID: report_id,
            ORG_UNIT: org_unit,
            PERIOD: period,
        }
        url = "%(base_url)s/dhis-web-reporting/generateHtmlReport.action?uid=%(report_id)s&pe=%(period)s&ou=%(org_unit)s" % query
        query["url"] = url
        logger.info("open report", extra=query)
        self.browser.visit(url)
        return get_html_table(self.browser.html, report_id)


PERIOD = "period"
ORG_UNIT = "org_unit"
REPORT_ID = "report_id"
BASE_URL = "base_url"
PASSWORD_FIELD = "j_password"
USERNAME_FIELD = "j_username"
