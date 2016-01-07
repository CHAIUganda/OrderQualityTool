import json
import os
from json import loads
import arrow
from arrow import now
from django.core.urlresolvers import reverse
from django.test import TestCase
from django_webtest import WebTest
from mock import patch, ANY
from webtest import Upload
from dashboard.helpers import WEB_BASED, REPORTING, MULTIPLE_ORDERS
from dashboard.models import Cycle, Score, DashboardUser, CycleFormulationScore


class HomeViewTestCase(WebTest):
    def test_correct_template(self):
        home = self.app.get('/', user="testuser")
        self.assertTemplateUsed(home, "home.html")

    def test_home_requires_login(self):
        home = self.app.get('/')
        self.assertEqual(302, home.status_code)


class DataImportViewTestCase(WebTest):
    def get_fixture_path(self, name):
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fixtures', name)
        return file_path

    @patch('dashboard.views.main.import_general_report.delay')
    def test_valid_form_starts_import_process(self, mock_method):
        user = DashboardUser.objects.create_superuser("a@a.com", "secret")
        cycle = 'Jan - Feb %s' % now().format("YYYY")
        url = '/import/'
        import_page = self.app.get(url, user=user)
        form = import_page.form
        form['cycle'] = cycle
        form['import_file'] = Upload(self.get_fixture_path("c.xlsx"))
        form.submit()
        mock_method.assert_called_with(ANY, cycle)


class FacilitiesReportingView(WebTest):
    def test_that_cycles_are_padded(self):
        cycle = 'Jan - Feb %s' % now().format("YYYY")
        CycleFormulationScore.objects.create(combination="DEFAULT", test=REPORTING, yes=50, no=50, cycle=cycle)
        url = "/api/test/submittedOrder"
        json_response = self.app.get(url, user="testuser").content.decode('utf8')
        data = loads(json_response)['values']
        self.assertIn({"reporting": 50, "cycle": cycle, "not_reporting": 50}, data)

    @patch("dashboard.views.api.now")
    def test_that_start_end_work(self, time_mock):
        time_mock.return_value = arrow.Arrow(2015, 12, 01)
        cycle = 'Jan - Feb 2015'
        cycle_2 = 'Mar - Apr 2015'
        Cycle.objects.create(title=cycle)
        url = "/api/test/submittedOrder?start=%s&end=%s" % (cycle, cycle_2)
        json_response = self.app.get(url, user="testuser").content.decode('utf8')
        data = loads(json_response)['values']
        self.assertEqual(len(data), 2)


class WebBasedReportingViewTestCase(WebTest):
    def test_that_cycles_are_padded(self):
        cycle = 'Jan - Feb %s' % now().format("YYYY")
        CycleFormulationScore.objects.create(combination="DEFAULT", test="WEB_BASED", yes=50, no=50, cycle=cycle)
        url = "/api/test/orderType"
        json_response = self.app.get(url, user="testuser").content.decode('utf8')
        data = loads(json_response)['values']
        self.assertIn({"web": 50, "cycle": cycle, "paper": 50}, data)

    @patch("dashboard.views.api.now")
    def test_that_start_end_work(self, time_mock):
        time_mock.return_value = arrow.Arrow(2015, 12, 01)
        cycle = 'Jan - Feb 2015'
        cycle_2 = 'Mar - Apr 2015'
        Cycle.objects.create(title=cycle)
        url = "/api/test/orderType?start=%s&end=%s" % (cycle, cycle_2)
        json_response = self.app.get(url, user="testuser").content.decode('utf8')
        data = loads(json_response)['values']
        self.assertEqual(len(data), 2)


class FacilitiesMultipleReportingViewTestCase(WebTest):
    def test_shows_all_facilities_that_report_multiple_times(self):
        cycle = 'Jan - Feb %s' % now().format("YYYY")
        Cycle.objects.create(title=cycle)
        url = "/api/test/facilitiesMultiple"
        json_response = self.app.get(url, user="testuser").content.decode('utf8')
        data = loads(json_response)['values']
        self.assertEqual(len(data), 1)


class BestDistrictReportingViewFor(WebTest):
    def test_best_performing_districts(self):
        Score.objects.create(name="F1", warehouse="W1", ip="I1", district="D1", REPORTING={"DEFAULT": "YES"},
                             WEB_BASED={"DEFAULT": "YES"}, pass_count=2, fail_count=0)
        Score.objects.create(name="F1", warehouse="W1", ip="I1", district="D2", REPORTING={"DEFAULT": "NO"},
                             WEB_BASED={"DEFAULT": "YES"}, pass_count=1, fail_count=1)
        url = reverse("ranking_best")
        json_response = self.app.get(url, user="testuser").content.decode('utf8')
        data = loads(json_response)['values']
        self.assertEquals('D1', data[0]['name'])
        self.assertEquals(100.0, data[0]['rate'])
        self.assertEquals('D2', data[1]['name'])
        self.assertEquals(50.0, data[1]['rate'])

    def test_best_performing_ips(self):
        Score.objects.create(name="F1", warehouse="W1", ip="I1", district="D1", REPORTING={"DEFAULT": "YES"},
                             WEB_BASED={"DEFAULT": "YES"}, pass_count=2, fail_count=0)
        Score.objects.create(name="F1", warehouse="W1", ip="I2", district="D2", REPORTING={"DEFAULT": "NO"},
                             WEB_BASED={"DEFAULT": "YES"}, pass_count=1, fail_count=1)
        url = reverse("ranking_best") + "?level=ip"
        json_response = self.app.get(url, user="testuser").content.decode('utf8')
        data = loads(json_response)['values']
        self.assertEquals('I1', data[0]['name'])
        self.assertEquals(100.0, data[0]['rate'])

    def test_best_performing_warehouses(self):
        Score.objects.create(name="F1", warehouse="W1", ip="I1", district="D1", REPORTING={"DEFAULT": "YES"},
                             WEB_BASED={"DEFAULT": "YES"}, pass_count=2, fail_count=0)
        Score.objects.create(name="F1", warehouse="W1", ip="I2", district="D2", REPORTING={"DEFAULT": "NO"},
                             WEB_BASED={"DEFAULT": "YES"}, pass_count=1, fail_count=1)
        url = reverse("ranking_best") + "?level=warehouse"
        json_response = self.app.get(url, user="testuser").content.decode('utf8')
        data = loads(json_response)['values']
        self.assertEquals('W1', data[0]['name'])
        self.assertAlmostEqual(75.0, data[0]['rate'])

    def test_best_performing_facilities(self):
        Score.objects.create(name="F1", warehouse="W1", ip="I1", district="D1", REPORTING={"DEFAULT": "YES"},
                             WEB_BASED={"DEFAULT": "YES"}, pass_count=2, fail_count=0)
        Score.objects.create(name="F2", warehouse="W1", ip="I2", district="D2", REPORTING={"DEFAULT": "NO"},
                             WEB_BASED={"DEFAULT": "YES"}, pass_count=1, fail_count=1)
        url = reverse("ranking_best") + "?level=facility"
        json_response = self.app.get(url, user="testuser").content.decode('utf8')
        data = loads(json_response)['values']
        self.assertEquals('F1', data[0]['name'])
        self.assertEquals(100.0, data[0]['rate'])

    def test_worst_performing_districts(self):
        Score.objects.create(name="F1", warehouse="W1", ip="I1", district="D1", REPORTING={"DEFAULT": "YES"},
                             WEB_BASED={"DEFAULT": "YES"}, pass_count=2, fail_count=0)
        Score.objects.create(name="F2", warehouse="W1", ip="I2", district="D2", REPORTING={"DEFAULT": "NO"},
                             WEB_BASED={"DEFAULT": "YES"}, pass_count=1, fail_count=1)
        url = reverse("ranking_worst")
        json_response = self.app.get(url, user="testuser").content.decode('utf8')
        data = loads(json_response)['values']
        self.assertEquals('D2', data[0]['name'])
        self.assertEquals(50.0, data[0]['rate'])

    def test_worst_performing_ips(self):
        Score.objects.create(name="F1", warehouse="W1", ip="I1", district="D1", REPORTING={"DEFAULT": "YES"},
                             WEB_BASED={"DEFAULT": "YES"}, pass_count=2, fail_count=0)
        Score.objects.create(name="F2", warehouse="W1", ip="I2", district="D2", REPORTING={"DEFAULT": "NO"},
                             WEB_BASED={"DEFAULT": "YES"}, pass_count=1, fail_count=1)
        url = reverse("ranking_worst") + "?level=ip"
        json_response = self.app.get(url, user="testuser").content.decode('utf8')
        data = loads(json_response)['values']
        self.assertEquals('I2', data[0]['name'])
        self.assertEquals(50.0, data[0]['rate'])

    def test_worst_performing_warehouses(self):
        Score.objects.create(name="F1", warehouse="W1", ip="I1", district="D1", REPORTING={"DEFAULT": "YES"},
                             WEB_BASED={"DEFAULT": "YES"}, pass_count=2, fail_count=0)
        Score.objects.create(name="F2", warehouse="W2", ip="I2", district="D2", REPORTING={"DEFAULT": "NO"},
                             WEB_BASED={"DEFAULT": "YES"}, pass_count=1, fail_count=1)
        url = reverse("ranking_worst") + "?level=warehouse"
        json_response = self.app.get(url, user="testuser").content.decode('utf8')
        data = loads(json_response)['values']
        self.assertEquals('W2', data[0]['name'])
        self.assertEquals(50.0, data[0]['rate'])

    def test_worst_performing_facilities(self):
        Score.objects.create(name="F1", warehouse="W1", ip="I1", district="D1", REPORTING={"DEFAULT": "YES"},
                             WEB_BASED={"DEFAULT": "YES"}, pass_count=2, fail_count=0)
        Score.objects.create(name="F2", warehouse="W2", ip="I2", district="D2", REPORTING={"DEFAULT": "NO"},
                             WEB_BASED={"DEFAULT": "YES"}, pass_count=1, fail_count=1)
        url = reverse("ranking_worst") + "?level=facility"
        json_response = self.app.get(url, user="testuser").content.decode('utf8')
        data = loads(json_response)['values']
        self.assertEquals('F2', data[0]['name'])
        self.assertEquals(50.0, data[0]['rate'])

    def test_worst_csv(self):
        Score.objects.create(name="F1", warehouse="W1", ip="I1", district="D1", REPORTING={"DEFAULT": "YES"},
                             WEB_BASED={"DEFAULT": "YES"}, pass_count=2, fail_count=0)
        Score.objects.create(name="F2", warehouse="W2", ip="I2", district="D2", REPORTING={"DEFAULT": "NO"},
                             WEB_BASED={"DEFAULT": "YES"}, pass_count=1, fail_count=1)
        url = reverse("ranking_worst_csv") + "?level=facility"
        csv = self.app.get(url, user="testuser").content.decode('utf8')
        expected = """facility,reporting rate
F2,50.0
F1,100.0
"""
        self.assertEquals(csv.replace("\r", ""), expected)

    def test_best_csv(self):
        Score.objects.create(name="F1", warehouse="W1", ip="I1", district="D1", REPORTING={"DEFAULT": "YES"},
                             WEB_BASED={"DEFAULT": "YES"}, pass_count=2, fail_count=0)
        Score.objects.create(name="F2", warehouse="W2", ip="I2", district="D2", REPORTING={"DEFAULT": "NO"},
                             WEB_BASED={"DEFAULT": "YES"}, pass_count=1, fail_count=1)
        url = reverse("ranking_best_csv") + "?level=facility"
        csv = self.app.get(url, user="testuser").content.decode('utf8')
        expected = """facility,reporting rate
F1,100.0
F2,50.0
"""
        self.assertEquals(csv.replace("\r", ""), expected)


class FacilityTestCycleScoresListViewTestCase(WebTest):
    def test_should_make_one_query(self):
        Score.objects.create(name='AIC Jinja Special Clinic', warehouse='warehouse', district='dis1', ip='ip',
                             REPORTING={"formulation1": "YES", "formulation2": "NO"}, pass_count=1, fail_count=1)
        with self.assertNumQueries(2):
            response = self.app.get(reverse("scores"))
            json_text = response.content.decode('utf8')
            data = json.loads(json_text)
            self.assertEqual(len(data['results']), 1)
            self.assertEqual(data['results'][0]['name'], 'AIC Jinja Special Clinic')
            self.assertEqual(data['results'][0]['warehouse'], 'warehouse')
            self.assertEqual(data['results'][0]['district'], 'dis1')
            self.assertEqual(data['results'][0]['ip'], 'ip')
            self.assertEqual(data['results'][0]['REPORTING'], {'formulation1': 'YES', 'formulation2': 'NO'})
