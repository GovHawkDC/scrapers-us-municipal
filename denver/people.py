import collections
import datetime
import re

from legistar.people import LegistarAPIPersonScraper, LegistarPersonScraper
from pupa.scrape import Person, Organization, Scraper

class DenverPersonScraper(LegistarAPIPersonScraper, Scraper):
    BASE_URL = 'https://webapi.legistar.com/v1/denver'
    WEB_URL = 'https://denver.legistar.com'
    TIMEZONE = 'US/Mountain'

    COMMITTEE_LIST = 'https://www.denvergov.org/content/denvergov/en/denver-city-council/council-committees.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.people = {}
        self.all_bodies = {}

        # https://webapi.legistar.com/v1/denver/BodyTypes
        # Mapping for body types to OCD orgs
        self.body_types = {
            'City Council': 'legislature',
            'Special Issues Marijuana': 'committee',
            'Special Issues: Green Roof Initiative': 'committee',
            'Administration': 'committee'
        }

    def scrape_bodies(self):
        for body in self.bodies():
            if body['BodyActiveFlag'] == 0:
                continue

            body_type = None
            if 'committee' in body['BodyName'].lower():
                body_type = 'committee'
            elif body['BodyTypeName'] in self.body_types:
                body_type = self.body_types[body['BodyTypeName']]

            org = Organization(
                name=body['BodyName'],
                classification=body_type,
            )

            org.add_source(self.COMMITTEE_LIST)
            # https://denver.legistar.com/DepartmentDetail.aspx?ID=34327&GUID=C7BB9AAF-7098-4F9F-8F40-D158899927A7&Search=

            self.all_bodies[body['BodyId']] = org
            yield org

    def scrape_people(self):
        people_url = 'https://webapi.legistar.com/v1/denver/Persons'
        for person in self.pages(people_url, item_key="PersonId"):
            print(person)
        # people_json = self.get(people_url).json()
        # for person in people_json:
        #     if person['PersonActiveFlag'] == 1:
        #         self.people[person['PersonId']] = person

    def scrape(self):
        # web_scraper = LegistarAPIPersonScraper(self,datadir="_data/denver")
        # city_council, = [body for body in self.bodies()
        #                  if body['BodyName'] == 'City Council']
        yield from self.scrape_bodies()
        # self.scrape_people()


        # terms = collections.defaultdict(list)