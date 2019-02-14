from pupa.scrape import Jurisdiction, Organization, Person

from .people import DenverPersonScraper
# from .events import DenverEventsScraper
from .bills import DenverBillScraper

import datetime


class Denver(Jurisdiction):
    division_id = 'ocd-division/country:us/state:co/place:denver'
    classification='government'
    name = 'Denver City Government'
    url =  'https://denver.legistar.com/'
    parties = [ {'name': 'Democrats' } ]

    scrapers = {
        "people": DenverPersonScraper,
        # "events": DenverEventsScraper,
        "bills": DenverBillScraper,
    }

    legislative_sessions = [
        {
            "identifier":"2018-2019",
            "name":"2018-2019 Regular Session",
            "start_date": "2018-01-01",
            "end_date": "2019-12-31"
        },
    ]

    def get_organizations(self):
        org = Organization(name="Denver City Council", classification="legislature")
        for x in range(1, 11):
            org.add_post(
                "Council District {}".format(x),
                "councilmember",
                division_id='ocd-division/country:us/state:co/place:denver/district:{}'.format(x))

            org.add_post(
                "At-large Council",
                "councilmember",
                division_id='ocd-division/country:us/state:co/place:denver'.format(x)
            )
        yield org



        city = Organization('City of Denver', classification='executive')
        city.add_post('Mayor', 'Mayor', division_id='ocd-division/country:us/state:co/place:denver')
        city.add_post('City Clerk', 'City Clerk', division_id='ocd-division/country:us/state:co/place:denver')

        yield city

        mayor = Person(name="Michael B. Hancock")
        mayor.add_term('Mayor',
                       'executive',
                       start_date=datetime.date(2011, 7, 18),
                       appointment=True)
                       #TODO: proper source
        mayor.add_source('https://en.wikipedia.org/wiki/Michael_Hancock_(Colorado_politician)')
        yield mayor
