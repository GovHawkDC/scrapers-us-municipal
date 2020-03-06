# encoding=utf-8
from pupa.scrape import Jurisdiction, Organization
from .events import {{ class_name }}EventScraper

class {{ class_name }}(Jurisdiction):
    division_id = "{{ocd_id}}"
    classification = "legislature"
    name = "{{city_name}}"
    url = "{{url}}"
    scrapers = {
        "events": {{ class_name }}EventScraper,
    }

    def get_organizations(self):
        org = Organization(name="{{ city_name }} Government", classification="legislature")
        yield org

