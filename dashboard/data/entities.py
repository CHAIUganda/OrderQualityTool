import attr
import pydash

from dashboard.helpers import *

TABLE_COLUMN_NEW_PREGNANT_PATIENTS = "ESTIMATED NUMBER OF NEW HIV+ PREGNANT WOMEN"
TABLE_COLUMN_NEW_PATIENTS = "ESTIMATED NUMBER OF NEW ART PATIENTS"
TABLE_COLUMN_QUANTITY_REQUIRED_FOR_CURRENT_PATIENTS = "QUANTITY REQUIRED FOR CURRENT PATIENTS"
TABLE_COLUMN_PACKS_ORDERED = "Packs Ordered"
TABLE_COLUMN_MONTHS_OF_STOCK_ON_HAND = "MONTHS OF STOCK ON-HAND"
TABLE_COLUMN_RECEIVED = "Quantity Recieved"
EXISTING = 'existing'
NEW = 'new'
TABLE_COLUMN_SUBCOUNTY = "Subcounty"
TABLE_COLUMN_REGION = "Region"
TABLE_COLUMN_FACILITY = "Facility"
TABLE_COLUMN_DISTRICT = "District"
TABLE_COLUMN_REGIMEN = "Regimen"
TABLE_COLUMN_OPENING_BALANCE = "Opening Balance"
TABLE_COLUMN_CLOSING_BALANCE = "Closing Balance"
TABLE_COLUMN_ART_CONSUMPTION = "ART Consumption"
TABLE_COLUMN_LOSES_ADJUSTMENTS = "Losses/Adjustments"
TABLE_COLUMN_NEW = "New"
TABLE_COLUMN_EXISTING = "Existing"


@attr.s(cmp=True, frozen=True)
class Location(object):
    facility = attr.ib()
    district = attr.ib()
    partner = attr.ib()
    warehouse = attr.ib()
    multiple = attr.ib(attr.Factory(lambda: ""))
    status = attr.ib(attr.Factory(lambda: ""))

    @staticmethod
    def migrate_from_dict(data):
        return Location(
            facility=data.get("name", ""),
            partner=data.get("IP", ""),
            district=data.get("District", ""),
            warehouse=data.get("Warehouse", ""),
            multiple=data.get("Multiple", ""),
            status=data.get("status", ""),
        )


@attr.s(cmp=True, frozen=True)
class RegimenLocationCombination(object):
    location = attr.ib()
    formulation = attr.ib()


@attr.s(cmp=True)
class Record(object):
    formulation = attr.ib()
    location = attr.ib()
    regimen_location = attr.ib()

    def as_dict_for_model(self):
        record = attr.asdict(self)
        del record["location"]
        del record["regimen_location"]
        return record


@attr.s(cmp=True)
class PatientRecord(Record):
    existing = attr.ib()
    new = attr.ib()

    def add(self, record):
        return PatientRecord(
            location=self.location,
            regimen_location=self.regimen_location,
            existing=as_int(record.existing) + as_int(self.existing),
            new=as_int(record.new) + as_int(self.new),
            formulation=self.formulation)

    @staticmethod
    def migrate_from_dict(data, location=None, regimen_location=None):
        return PatientRecord(
            location=location,
            regimen_location=regimen_location,
            existing=data.get(EXISTING),
            formulation=data.get(FORMULATION),
            new=data.get(NEW),
        )


def as_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


@attr.s(cmp=True)
class ConsumptionRecord(Record):
    opening_balance = attr.ib()
    quantity_received = attr.ib()
    consumption = attr.ib()
    loses_adjustments = attr.ib()
    closing_balance = attr.ib()
    months_of_stock_on_hand = attr.ib()
    quantity_required_for_current_patients = attr.ib()
    estimated_number_of_new_patients = attr.ib()
    estimated_number_of_new_pregnant_women = attr.ib()
    packs_ordered = attr.ib()
    days_out_of_stock = attr.ib()

    @staticmethod
    def migrate_from_dict(data, location=None, regimen_location=None):
        return ConsumptionRecord(
            location=location,
            regimen_location=regimen_location,
            formulation=data.get(FORMULATION),
            opening_balance=data.get(OPENING_BALANCE),
            quantity_received=data.get(QUANTITY_RECEIVED),
            consumption=data.get(COMBINED_CONSUMPTION),
            loses_adjustments=data.get(LOSES_ADJUSTMENTS),
            closing_balance=data.get(CLOSING_BALANCE),
            months_of_stock_on_hand=data.get(MONTHS_OF_STOCK_ON_HAND),
            quantity_required_for_current_patients=data.get(QUANTITY_REQUIRED_FOR_CURRENT_PATIENTS),
            estimated_number_of_new_patients=data.get(ESTIMATED_NUMBER_OF_NEW_ART_PATIENTS),
            estimated_number_of_new_pregnant_women=data.get(ESTIMATED_NUMBER_OF_NEW_PREGNANT_WOMEN),
            days_out_of_stock=data.get(DAYS_OUT_OF_STOCK),
            packs_ordered=data.get(PACKS_ORDERED),
        )

    def add(self, record):
        opening_balance = as_int(self.opening_balance) + as_int(record.opening_balance)
        quantity_received = as_int(self.quantity_received) + as_int(record.quantity_received)
        consumption = as_int(self.consumption) + as_int(record.consumption)
        loses_adjustments = as_int(self.loses_adjustments) + as_int(record.loses_adjustments)
        closing_balance = as_int(self.closing_balance) + as_int(record.closing_balance)
        months_of_stock_on_hand = as_int(self.months_of_stock_on_hand) + as_int(record.months_of_stock_on_hand)
        quantity_required_for_current_patients = as_int(self.quantity_required_for_current_patients) + as_int(
            record.quantity_required_for_current_patients)
        estimated_number_of_new_patients = as_int(self.estimated_number_of_new_patients) + as_int(
            record.estimated_number_of_new_patients)
        number_of_new_pregnant_women = as_int(self.estimated_number_of_new_pregnant_women) + as_int(
            record.estimated_number_of_new_pregnant_women)
        packs_ordered = as_int(self.packs_ordered) + as_int(record.packs_ordered)
        days_out_of_stock = as_int(self.days_out_of_stock) + as_int(record.days_out_of_stock)
        return ConsumptionRecord(
            location=self.location,
            regimen_location=self.regimen_location,
            formulation=self.formulation,
            opening_balance=opening_balance,
            quantity_received=quantity_received,
            consumption=consumption,
            loses_adjustments=loses_adjustments,
            closing_balance=closing_balance,
            months_of_stock_on_hand=months_of_stock_on_hand,
            quantity_required_for_current_patients=quantity_required_for_current_patients,
            estimated_number_of_new_patients=estimated_number_of_new_patients,
            estimated_number_of_new_pregnant_women=number_of_new_pregnant_women,
            packs_ordered=packs_ordered,
            days_out_of_stock=days_out_of_stock,
        )


@attr.s
class HtmlDataImportRecord(object):
    warehouse = attr.ib()
    report_type = attr.ib()
    data = attr.ib()
    location = attr.ib(None)

    def get_facility(self):
        return self.data.get(TABLE_COLUMN_FACILITY)

    def get_region(self):
        return self.data.get(TABLE_COLUMN_REGION)

    def get_subcounty(self):
        return self.data.get(TABLE_COLUMN_SUBCOUNTY)

    def get_district(self):
        return self.data.get(TABLE_COLUMN_DISTRICT)

    def get_opening_balance(self):
        return self.data.get(TABLE_COLUMN_OPENING_BALANCE)

    def get_quantity_received(self):
        return self.data.get(TABLE_COLUMN_RECEIVED)

    def get_consumption(self):
        return self.data.get(TABLE_COLUMN_ART_CONSUMPTION)

    def get_loses_adjustments(self):
        return self.data.get(TABLE_COLUMN_LOSES_ADJUSTMENTS)

    def get_closing_balance(self):
        return self.data.get(TABLE_COLUMN_CLOSING_BALANCE)

    def get_months_of_stock_on_hand(self):
        return self.data.get(TABLE_COLUMN_MONTHS_OF_STOCK_ON_HAND)

    def get_quantity_required_for_current_patients(self):
        return self.data.get(TABLE_COLUMN_QUANTITY_REQUIRED_FOR_CURRENT_PATIENTS)

    def get_number_of_new_art_patients(self):
        return self.data.get(TABLE_COLUMN_NEW_PATIENTS)

    def get_number_of_new_pregnant_patients(self):
        return self.data.get(TABLE_COLUMN_NEW_PREGNANT_PATIENTS)

    def get_packs_ordered(self):
        return self.data.get(TABLE_COLUMN_PACKS_ORDERED)

    def has_facility_without_region(self):
        return TABLE_COLUMN_REGION not in self.data and TABLE_COLUMN_FACILITY in self.data

    def build_location(self, partner_mapping):
        facility = self.get_facility()
        district = self.get_district()

        if self.has_facility_without_region():
            location_spread = self.get_facility().split("/")
            if len(location_spread) > 5:
                facility = location_spread[5]
                district = location_spread[3]
        partner = partner_mapping.get(facility, "Unknown")
        return Location(
            facility=facility,
            district=district,
            partner=partner,
            warehouse=self.warehouse
        )

    def build_patient_record(self):
        formulation = self.data.get(TABLE_COLUMN_REGIMEN)
        rl = RegimenLocationCombination(location=self.location, formulation=formulation)
        return PatientRecord(location=self.location,
                             regimen_location=rl,
                             existing=self.data.get(TABLE_COLUMN_EXISTING),
                             new=self.data.get(TABLE_COLUMN_NEW),
                             formulation=formulation)

    def build_consumption_record(self):
        formulation = self.data.get("REGIMEN")
        rl = RegimenLocationCombination(location=self.location, formulation=formulation)
        return ConsumptionRecord(location=self.location,
                                 regimen_location=rl,
                                 opening_balance=self.get_opening_balance(),
                                 quantity_received=self.get_quantity_received(),
                                 consumption=self.get_consumption(),
                                 loses_adjustments=self.get_loses_adjustments(),
                                 closing_balance=self.get_closing_balance(),
                                 months_of_stock_on_hand=self.get_months_of_stock_on_hand(),
                                 quantity_required_for_current_patients=self.get_quantity_required_for_current_patients(),
                                 estimated_number_of_new_patients=self.get_number_of_new_art_patients(),
                                 estimated_number_of_new_pregnant_women=self.get_number_of_new_pregnant_patients(),
                                 packs_ordered=self.get_packs_ordered(),
                                 days_out_of_stock=None,
                                 formulation=formulation)


@attr.s
class ExcelDataImportRecord(object):
    data = attr.ib()
    location = attr.ib(None)

    def build_location(self):
        facility = self.data.get(NAME)
        district = self.data.get(DISTRICT)
        partner = self.data.get(IP)
        warehouse = self.data.get(WAREHOUSE)
        status = self.data.get(STATUS)
        multiple = self.data.get(MULTIPLE)

        return Location(
            facility=facility,
            district=district,
            partner=partner,
            warehouse=warehouse,
            status=status,
            multiple=multiple,
        )

    def build_patient_record(self):
        formulation = self.data.get(FORMULATION)
        rl = RegimenLocationCombination(location=self.location, formulation=formulation)
        return PatientRecord.migrate_from_dict(self.data, location=self.location,
                                               regimen_location=rl)

    def build_consumption_record(self):
        formulation = self.data.get(FORMULATION)
        rl = RegimenLocationCombination(location=self.location, formulation=formulation)
        return ConsumptionRecord.migrate_from_dict(self.data, self.location, rl)


@attr.s
class ReportOutput(object):
    report = attr.ib()
    output = attr.ib()


@attr.s
class LocationData(object):
    location = attr.ib()
    c_count = attr.ib()
    a_count = attr.ib()
    p_count = attr.ib()
    a_records = attr.ib()
    c_records = attr.ib()
    p_records = attr.ib()

    @staticmethod
    def migrate_from_dict(data):
        c_records = pydash.map_(data.get(C_RECORDS, []), ConsumptionRecord.migrate_from_dict)
        a_records = pydash.map_(data.get(A_RECORDS, []), PatientRecord.migrate_from_dict)
        p_records = pydash.map_(data.get(P_RECORDS, []), PatientRecord.migrate_from_dict)
        location = Location.migrate_from_dict(data)
        c_count = data.get(C_COUNT, len(c_records))
        a_count = data.get(A_COUNT, len(a_records))
        p_count = data.get(P_COUNT, len(p_records))
        return LocationData(
            location=location,
            c_records=c_records,
            a_records=a_records,
            p_records=p_records,
            c_count=c_count,
            a_count=a_count,
            p_count=p_count
        )


def get_real_facility_name(facility_name, district_name):
    if facility_name:
        template = "_%s" % district_name
        return facility_name.replace(template, "")
    else:
        return facility_name


def enrich_location_data(location, report):
    c_records = report.cs.get(location, [])
    a_records = report.ads.get(location, [])
    p_records = report.pds.get(location, [])

    return LocationData(
        location=location,
        c_count=len(c_records),
        a_count=len(a_records),
        p_count=len(p_records),
        c_records=c_records,
        p_records=p_records,
        a_records=a_records
    )