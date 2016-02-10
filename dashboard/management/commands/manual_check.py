import json

import djclick as click
from termcolor import colored

from dashboard.helpers import *
from dashboard.models import Score


def make_cond(cond):
    cond = json.dumps(cond)[1:-1]  # remove '{' and '}'
    return (cond).replace(": ", ":")  # avoid '\"'


@click.command()
def command():
    perform_checks()


def perform_checks():
    cycle = "Jul - Aug 2015"
    cycle2 = cycle
    checks = [
        {'combination': DEFAULT, 'test': ORDER_FORM_FREE_OF_GAPS, 'cycle': cycle, 'expected': 46.2, YES: 820, NO: 615, NOT_REPORTING: 365},
        # {'combination': F3, 'test': ORDER_FORM_FREE_OF_NEGATIVE_NUMBERS, 'cycle': cycle, 'expected': 70.9, YES: 1000, NO: 100, NOT_REPORTING: 1000},
        # {'combination': F3, 'test': CONSUMPTION_AND_PATIENTS, 'cycle': cycle, 'expected': 9.8},
        # {'combination': F3, 'test': DIFFERENT_ORDERS_OVER_TIME, 'cycle': cycle2, 'expected': 47.7, YES: 1000, NO: 1000, NOT_REPORTING: 100},
        {'combination': F3, 'test': STABLE_CONSUMPTION, 'cycle': cycle2, 'expected': 8.8, YES: 114, NO: 252, NOT_REPORTING: 1454},
        {'combination': F3, 'test': WAREHOUSE_FULFILMENT, 'cycle': cycle2, 'expected': 32.4, YES: 345, NO: 366, NOT_REPORTING: 1109},
        {'combination': F3, 'test': STABLE_PATIENT_VOLUMES, 'cycle': cycle2, 'expected': 15.6, YES: 213, NO: 156, NOT_REPORTING: 1451},
        {'combination': DEFAULT, 'test': GUIDELINE_ADHERENCE_ADULT_1L, 'cycle': cycle, 'expected': 35.3, YES: 643, NO: 737, NOT_REPORTING: 440},
        {'combination': DEFAULT, 'test': GUIDELINE_ADHERENCE_ADULT_2L, 'cycle': cycle, 'expected': 50.5, YES: 920, NO: 274, NOT_REPORTING: 626},
        {'combination': DEFAULT, 'test': GUIDELINE_ADHERENCE_PAED_1L, 'cycle': cycle, 'expected': 28.9, YES: 526, NO: 752, NOT_REPORTING: 542},
    ]
    for check in checks:
        if check.get('combination') == DEFAULT:
            yes_condition = {DEFAULT: YES}
            no_condition = {DEFAULT: NO}
            not_reporting_condition = {(DEFAULT): NOT_REPORTING}
        else:
            yes_condition = {check.get('combination'): YES}
            no_condition = {check.get('combination'): NO}
            not_reporting_condition = {check.get('combination'): NOT_REPORTING}
        for key, condition in {YES: yes_condition, NO: no_condition, NOT_REPORTING: not_reporting_condition}.items():
            test_description = "%s %s" % (check['test'], key)
            filter_key = "%s__icontains" % check.get('test')
            filter_by = {filter_key: make_cond(condition)}
            count = Score.objects.filter(cycle=check['cycle'], **filter_by).count()
            expected = check[key]
            actual = count
            if expected == actual:
                print colored(test_description + " Passed", "green")
            else:
                tolerance = 10
                diff = abs(float(expected) - float(actual))
                c = "yellow" if diff <= tolerance else "red"
                print colored(test_description + " Failed", c), colored("Got %s instead of %s " % (actual, expected), c), colored("diff: %s" % diff, "blue")
