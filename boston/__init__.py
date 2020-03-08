# encoding=utf-8
from pupa.scrape import Jurisdiction, Organization
from .events import BostonEventScraper


class Boston(Jurisdiction):
    division_id = "ocd-division/country:us/state:ma/place:boston"
    classification = "legislature"
    name = "Boston"
    url = "Boston"
    scrapers = {
        "events": BostonEventScraper,
    }

    def get_organizations(self):
        org = Organization(name="Boston Government", classification="legislature")
        yield org