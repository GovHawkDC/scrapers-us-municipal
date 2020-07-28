# encoding=utf-8
from pupa.scrape import Jurisdiction, Organization
from .events import IndianapolisEventScraper
from .bills import IndianapolisBillScraper


class Indianapolis(Jurisdiction):
    division_id = "ocd-division/country:us/state:in/county:marion/place:indianapolis"
    classification = "government"
    name = "City of Indianapolis"
    url = "https://www.indy.gov/"
    scrapers = {
        "events": IndianapolisEventScraper,
        "bills": IndianapolisBillScraper,
    }

    def get_organizations(self):
        #REQUIRED: define an organization using this format
        #where org_name is something like Seattle City Council
        #and classification is described here:
        org = Organization(name="org_name", classification="legislature")

        # OPTIONAL: add posts to your organizaion using this format,
        # where label is a human-readable description of the post (eg "Ward 8 councilmember")
        # and role is the position type (eg councilmember, alderman, mayor...)
        # skip entirely if you're not writing a people scraper.
        org.add_post(label="position_description", role="position_type")

        #REQUIRED: yield the organization
        yield org
