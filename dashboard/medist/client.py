import attr
import pygogo
import requests
from dynamic_preferences.registries import global_preferences_registry
from pydash import py_
from requests.auth import HTTPBasicAuth

from dashboard.data.entities import Location
from dashboard.utils import log_formatter, should_log_time

logger = pygogo.Gogo(__name__, low_formatter=log_formatter).get_logger()
logger.setLevel("INFO" if should_log_time() else "ERROR")


def parse_warehouse(warehouse):
    return "".join([word[0] for word in warehouse.split(" ")])


class DHIS2APIClient(object):

    def __init__(self):
        global_preferences = global_preferences_registry.manager()
        username = global_preferences.get("DHIS2_Settings__DHIS2_USERNAME")
        password = global_preferences.get("DHIS2_Settings__DHIS2_PASSWORD")
        self.base_url = global_preferences.get("DHIS2_Settings__DHIS2_URL")
        logger.debug(
            "creating dhis2 client", extra={"url": self.base_url, "username": username}
        )
        self.auth = HTTPBasicAuth(username, password)

    def get_children(self, org_unit):
        url = "%s/api/organisationUnits/%s.json?fields=children[id,name],id,name,level" % (
            self.base_url, org_unit
        )
        response = requests.get(url, auth=self.auth)
        logger.debug(
            "dhis2 api request", extra={"url": url, "status": response.status_code}
        )
        return [unit.get("id") for unit in response.json().get("children", [])]

    def get_locations(self):
        filter = "filter=name:eq:ARVs%20Warehouse"
        fields = "fields=id,name,organisationUnitGroups[id,name,organisationUnits[id,name,ancestors[id,name,level]]]"
        url = "%s/api/organisationUnitGroupSets.json?%s&%s" % (
            self.base_url, filter, fields
        )
        # url = "%s/api/organisationUnits.json?fields=ancestors[name,level],id,name&filter=level:gte:5&paging=false" % self.base_url

        response = requests.get(url, auth=self.auth)
        logger.debug(
            "dhis2 api request", extra={"url": url, "status": response.status_code}
        )
        data = response.json().get("organisationUnitGroupSets", [])[0]
        org_units = []
        for organisation_unit_group in data.get("organisationUnitGroups"):
            warehouse = organisation_unit_group.get("name")
            units = organisation_unit_group.get("organisationUnits")
            for unit in units:
                unit["warehouse"] = parse_warehouse(warehouse)
            org_units.extend(units)
        logger.debug("got orgUnits from dhis2", extra={"url": url, "count": len(data)})
        return org_units


def dhis2_facility_as_location(
    partner_mapping, locations_that_are_reporting, locations_reporting_multiple_times
):

    def f(facility_dict):
        name = facility_dict.get("name", "")
        new_location = Location(
            facility=name,
            district=py_(facility_dict.get("ancestors", [])).find(
                {"level": 3}
            ).value().get(
                "name"
            ),
            partner=partner_mapping.get(name, "Unknown"),
            warehouse=facility_dict.get("warehouse"),
        )
        reference_location = locations_that_are_reporting.get(new_location, None)
        location_has_multiple = locations_reporting_multiple_times.get(
            new_location, None
        )
        if reference_location:
            new_location = attr.evolve(new_location, status="Reporting")
            if location_has_multiple:
                new_location = attr.evolve(new_location, multiple="multiple orders")
        else:
            new_location = attr.evolve(
                new_location, status="Not Reporting", multiple="not"
            )

        return new_location

    return f


def get_all_locations(
    partner_mapping, locations_that_are_reporting, locations_reporting_multiple_times
):
    all_facilities = DHIS2APIClient().get_locations()
    return list(
        map(
            dhis2_facility_as_location(
                partner_mapping,
                locations_that_are_reporting,
                locations_reporting_multiple_times,
            ),
            all_facilities,
        )
    )
