import pydash

from dashboard.data.utils import values_for_records, QCheck
from dashboard.helpers import *


class NegativeNumbersQualityCheck(QCheck):
    test = ORDER_FORM_FREE_OF_NEGATIVE_NUMBERS
    combinations = [{NAME: F1, CONSUMPTION_QUERY: F1_QUERY},
                    {NAME: F2, CONSUMPTION_QUERY: F2_QUERY},
                    {NAME: F3, CONSUMPTION_QUERY: F3_QUERY}]

    fields = [OPENING_BALANCE,
              QUANTITY_RECEIVED,
              PMTCT_CONSUMPTION,
              ART_CONSUMPTION,
              ESTIMATED_NUMBER_OF_NEW_PREGNANT_WOMEN,
              ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS]

    def for_each_facility(self, data, combination, previous_cycle_data=None):
        df1_records = self.get_consumption_records(data, combination[CONSUMPTION_QUERY])
        values = values_for_records(self.fields, df1_records)
        all_cells_not_negative = pydash.every(values,
                                              lambda x: x is None or x >= 0 )
        if len(df1_records) == 0:
            return NOT_REPORTING
        return YES if all_cells_not_negative else NO

    def get_consumption_records(self, data, formulation_name):
        records = data.get(C_RECORDS, [])
        return pydash.chain(records).reject(
            lambda x: formulation_name not in x[FORMULATION]
        ).value()
