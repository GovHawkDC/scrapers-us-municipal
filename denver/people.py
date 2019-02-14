import collections
import datetime
import re
import pytz

from legistar.people import LegistarAPIPersonScraper, LegistarPersonScraper
from pupa.scrape import Person, Organization, Scraper, Membership

class DenverPersonScraper(LegistarAPIPersonScraper, Scraper):
    BASE_URL = 'https://webapi.legistar.com/v1/denver'
    WEB_URL = 'https://denver.legistar.com'
    TIMEZONE = 'US/Mountain'

    COMMITTEE_LIST = 'https://www.denvergov.org/content/denvergov/en/denver-city-council/council-committees.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.all_people = {}
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

            # 276 is the "GO Bond" committee which flips in and out
            # so go ahead and always list it
            if body['BodyActiveFlag'] == 0 and body['BodyId'] != 276:
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

            self.all_bodies[body['BodyId']] = org
            yield org

    def scrape_body_membership(self):
        office_records_url = self.BASE_URL + '/OfficeRecords'
        now = pytz.timezone(self.TIMEZONE).localize(datetime.datetime.now())

        for row in self.pages(office_records_url, item_key="OfficeRecordId"):
            end_date = self.parse_iso(row['OfficeRecordEndDate'])

            # Due to data errors, there are a live few memberships in
            # dead committees.
            bad_bodies = [235]
            if row['OfficeRecordBodyId'] in bad_bodies:
                continue

            if end_date > now:
                person = self.all_people[row['OfficeRecordPersonId']]
                org = self.all_bodies[row['OfficeRecordBodyId']]
                start_date = self.parse_iso(row['OfficeRecordStartDate'])

                membership = Membership(
                    start_date=start_date,
                    end_date=end_date,
                    post_id=row['OfficeRecordGuid'],
                    role=row['OfficeRecordMemberType'],
                    person_id=person._id,
                    person_name=row['OfficeRecordFullName'],
                    organization_id=org._id)

                yield membership


    def scrape_people(self):
        people_url = self.BASE_URL + '/Persons'
        for row in self.pages(people_url, item_key="PersonId"):
            if row['PersonActiveFlag'] == 0:
                continue

            person = Person(
                name=row['PersonFullName'],
                primary_org="legislature",
            )

            person.add_source('https://www.denvergov.org/content/denvergov/en/denver-city-council/council-members.html', note="Council Page")

            person.extras = {
                'family_name': row['PersonFirstName'],
                'given_name': row['PersonLastName'],
                'guid': row['PersonGuid'],
            }
            self.all_people[row['PersonId']] = person
            yield person

    # they sometimes post microseconds, sometimes not
    def parse_iso(self, isodate):
        try:
            isodate = datetime.datetime.strptime(isodate, '%Y-%m-%dT%H:%M:%S.%f')
        except ValueError:
            isodate = datetime.datetime.strptime(isodate, '%Y-%m-%dT%H:%M:%S')
        isodate = pytz.timezone(self.TIMEZONE).localize(isodate)
        return isodate

    def scrape(self):

        yield from self.scrape_bodies()
        yield from self.scrape_people()
        yield from self.scrape_body_membership()
