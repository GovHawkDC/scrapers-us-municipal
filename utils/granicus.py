from pupa.scrape import Event, VoteEvent, Scraper
from pupa.utils import _make_pseudo_id
import datetime
import itertools
import pytz
import requests
import re
import lxml.html


class GranicusScraper():
    BASE_URL = ""
    TIMEZONE = ""
    s = requests.Session()

    def session(self, action_date):
        return str(action_date.year)

    def scrape(self, window=3):
        page = lxml.html.fromstring(requests.get(self.BASE_URL).content)
        page.make_links_absolute(self.BASE_URL)
        self.info(self.BASE_URL)
        yield from self.scrape_upcoming(page)

        yield from self.scrape_past(page, window)

    def scrape_upcoming(self, page):

        for row in page.xpath('//table[@id="upcoming"]/tbody/tr'):
            event_name = row.xpath('td[contains(@headers,"EventName")]/text()')[0].strip()
            # inside the date td is a display:none span w/ the unixtime.
            event_date =  row.xpath('td[contains(@headers,"EventDate")]/span[1]/text()')[0].strip()
            event_date = datetime.datetime.utcfromtimestamp(int(event_date))
            event_date = self.TIMEZONE.localize(event_date)

            event = Event(name=event_name,
                        start_date=event_date,
                        # description=description,
                        location_name="TBD",
                        )

            if row.xpath('.//a[contains(text(), "Agenda")]'):
                agenda_url = row.xpath('.//a[contains(text(), "Agenda")]/@href')[0]
                event.add_document('Agenda', agenda_url)

            event.add_source(self.BASE_URL)

            print(event)

            yield event
    
    def scrape_past(self, page, window):

        for row in page.xpath('//table[@id="archive"]/tbody/tr'):
            event_name = row.xpath('string(td[contains(@headers,"Name")])').strip()
            # inside the date td is a display:none span w/ the unixtime.
            event_date =  row.xpath('td[contains(@headers,"Date")]/span[1]/text()')[0].strip()
            event_date = datetime.datetime.utcfromtimestamp(int(event_date))
            event_date = self.TIMEZONE.localize(event_date)

            event = Event(name=event_name,
                        start_date=event_date,
                        # description=description,
                        location_name="TBD",
                        )

            if row.xpath('.//a[contains(text(), "Agenda")]'):
                url = row.xpath('.//a[contains(text(), "Agenda")]/@href')[0]
                event.add_document('Agenda', url)

            if row.xpath('.//a[contains(text(), "Minutes")]'):
                url = row.xpath('.//a[contains(text(), "Minutes")]/@href')[0]
                event.add_document('Minutes', url)

            if row.xpath('.//a[contains(text(), "MP4")]'):
                url = row.xpath('.//a[contains(text(), "MP4")]/@href')[0]
                event.add_media_link("Video", url, 'video/mp4')

            # TODO: Video and extracting that link from the js popup

            event.add_source(self.BASE_URL)
            print(event)

            yield event