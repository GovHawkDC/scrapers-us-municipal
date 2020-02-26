# encoding=utf-8
from pupa.scrape import Jurisdiction, Organization, Person

from .events import HoustonEventScraper
from .bills import HoustonBillScraper

import datetime


class Houston(Jurisdiction):
    division_id = "ocd-division/country:us/state:tx/place:houston"
    classification = "government"
    name = "Houston"
    timezone = "America/New_York"
    url = "https://pittsburgh.legistar.com"

    scrapers = {
        "events": HoustonEventScraper,
        "bills": HoustonBillScraper,
    }

    legislative_sessions = []

    for year in range(2001, 2030):
        legislative_sessions.append({"identifier": str(year),
                                     "name": str(year) + " Session",
                                     "start_date": str(year) + "-01-01",
                                     "end_date": str(year) + "-12-31"})

    def get_organizations(self):
        org = Organization(name="Houston City Council", classification="legislature")
        # org.add_source("https://google.com")
        # # for x in range(1, 10):
        # #     org.add_post(
        # #         "District {}".format(x),
        # #         "Councilmember",
        # #         division_id="ocd-division/country:us/state:pa/place:pittsburgh/council_district:{}".format(x))
        yield org

        # standing_committee = Organization(name="Standing Committee", classification="committee")
        # standing_committee.add_source("http://pittsburghpa.gov/council/standing-committees", note="web")
        # yield standing_committee

        # mayor = Organization(name="Mayor", classification="executive")
        # mayor.add_post("Mayor", "Mayor", division_id="ocd-division/country:us/state:tx/place:houston")
        # mayor.add_source("http://pittsburghpa.gov/mayor/index.html", note="web")
        # yield mayor
