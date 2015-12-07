from django.core.urlresolvers import reverse
from django_webtest import WebTest

from dashboard.checks.order_form_free_of_gaps import OrderFormFreeOfGaps
from dashboard.models import FacilityCycleRecord, FacilityConsumptionRecord, AdultPatientsRecord, PAEDPatientsRecord
from locations.models import Facility


class OrderFormFreeOfGapsViewTestCase(WebTest):
    url_name = 'order_form_free_of_gaps'

    def test_url_setup(self):
        url = reverse(self.url_name)
        response = self.app.get(url, user="testuser")
        self.assertEqual(200, response.status_code)

    def test_logic(self):
        names = ["FA1", "FA2", "FA3"]
        names_without_data = ["FA4", "FA5"]
        consumption_regimens = ["CREG-%s" % n for n in range(1, 26)]
        adult_regimens = ["AREG-%s" % n for n in range(1, 23)]
        paed_regimens = ["PREG-%s" % n for n in range(1, 9)]
        cycle = "Jan - Feb 2013"
        consumption_data = {}
        consumption_data['opening_balance'] = 3
        consumption_data['quantity_received'] = 4.5
        consumption_data['pmtct_consumption'] = 4.5
        consumption_data['art_consumption'] = 4.5
        consumption_data['loses_adjustments'] = 4.5
        consumption_data['closing_balance'] = 4.5
        consumption_data['months_of_stock_of_hand'] = 4
        consumption_data['quantity_required_for_current_patients'] = 4.5
        consumption_data['estimated_number_of_new_patients'] = 4.5
        consumption_data['estimated_number_of_new_pregnant_women'] = 4.5
        consumption_data['total_quantity_to_be_ordered'] = 4.5
        consumption_data['notes'] = None
        for name in names:
            facility, _ = Facility.objects.get_or_create(name=name)
            record, _ = FacilityCycleRecord.objects.get_or_create(cycle=cycle, facility=facility)
            consumption_data['facility_cycle'] = record
            for reg in consumption_regimens:
                consumption_data['formulation'] = reg
                FacilityConsumptionRecord.objects.create(**consumption_data)
            for reg in adult_regimens:
                AdultPatientsRecord.objects.create(facility_cycle=record, formulation=reg, existing=1.4, new=10.0)
            for reg in paed_regimens:
                PAEDPatientsRecord.objects.create(facility_cycle=record, formulation=reg, existing=3, new=12.0)

        for name in names_without_data:
            facility, _ = Facility.objects.get_or_create(name=name)
            record, _ = FacilityCycleRecord.objects.get_or_create(cycle=cycle, facility=facility)

        score = OrderFormFreeOfGaps().run(cycle)
        print score
        self.assertEqual(cycle, score.cycle)
        self.assertEqual(60.0, score.yes)
        self.assertEqual(0.0, score.no)
        self.assertEqual(40.0, score.not_reporting)