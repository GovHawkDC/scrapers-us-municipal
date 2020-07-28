import datetime
import pytz
from lxml import etree
from pupa.scrape import Scraper
from pupa.scrape import Event


class IndianapolisEventScraper(Scraper):
    TIMEZONE = pytz.timezone('America/Indiana/Indianapolis')

    def scrape(self):
        # http://calendar.indy.gov/Eventlist.aspx?fromdate=7/1/2020&todate=8/31/2020&display=Month&view=Grid&type=public&download=download&dlType=XML

        url = 'http://calendar.indy.gov/Eventlist.aspx?fromdate=7/1/2020&todate=8/31/2020&display=Month&view=Grid&type=public&download=download&dlType=XML'
        page = self.get(url).content
        page = etree.fromstring(page)


        for row in page.xpath('//Event'):
            event_name = row.xpath('string(EventName)')
            event_desc = row.xpath('string(EventDescription)')
            start_date = row.xpath('string(StartDate)')
            start_time = row.xpath('string(StartTime)')

            event_loc = "See Description"

            event_start = self.parse_date_fields(
                row.xpath('string(StartDate)'),
                row.xpath('string(StartTime)')
            )

            event_end = self.parse_date_fields(
                row.xpath('string(EndDate)'),
                row.xpath('string(EndTime)')
            )

            event = Event(
                name=event_name,
                start_date=event_start,
                end_date = event_end,
                description=event_desc,
                location_name=event_loc,
            )

            contact = row.xpath('string(ContactName)')
            if contact != '':
                event.add_person(
                    name=contact,
                    note="Contact"
                )

            event.add_source('http://calendar.indy.gov/')
            yield event

    def parse_date_fields(self, day, time):
        if time != '':
            full_date = '{} {}'.format(day, time)
            return self.TIMEZONE.localize(
                datetime.datetime.strptime(full_date, "%m/%d/%Y %I:%M %p")
            )
        else:
            return self.TIMEZONE.localize(
                datetime.datetime.strptime(day, "%m/%d/%Y")
            )                