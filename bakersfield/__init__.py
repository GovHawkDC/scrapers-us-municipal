# encoding=utf-8
from pupa.scrape import Jurisdiction, Organization
from .events import BakersfieldEventScraper

class Bakersfield(Jurisdiction):
    division_id = "ocd-division/country:us/state:ca/place:bakersfield"
    classification = "legislature"
    name = "Bakersfield"
    url = "https://www.cityofwestminster.us/Government/CityCouncil"
    scrapers = {
        "events": BakersfieldEventScraper,
    }

    def get_organizations(self):
        org = Organization(name="Bakersfield City Government", classification="legislature")
        yield org

