from pupa.scrape import Event, VoteEvent, Scraper
from pupa.utils import _make_pseudo_id
import datetime
import itertools
import pytz
import requests
import re
import lxml.html


class IQ2MScraper():
    BASE_URL = ""
    TIMEZONE = ""
    s = requests.Session()

    def session(self, action_date):
        return str(action_date.year)

    def scrape(self, window=3):
        print("SCRAPE CITY")
        year = datetime.datetime.today().year
        calendar_url = '{}/Citizens/Calendar.aspx?From=1/1/{}&To=12/31/{}'.format(self.BASE_URL, year, year)

        page = lxml.html.fromstring(requests.get(calendar_url).content)
        page.make_links_absolute(self.BASE_URL)

        for row in page.xpath('//div[contains(@class, "MeetingRow")]'):
            # event_date = row.xpath('div[contains(@class, "RowTop")]/div[contains(@class, "RowLink")]/a/text()')[0].strip()
            event_url = row.xpath('div[contains(@class, "RowTop")]/div[contains(@class, "RowLink")]/a/@href')[0].strip()
            yield from self.scrape_event_page(event_url)

    def scrape_event_page(self, url):
        self.info(url)
        page = lxml.html.fromstring(requests.get(url).content)
        page.make_links_absolute(self.BASE_URL)

        event_group = page.xpath('//span[@id="ContentPlaceholder1_lblMeetingGroup"]/text()')[0].strip()
        event_type = page.xpath('//span[@id="ContentPlaceholder1_lblMeetingType"]/text()')[0].strip()
        # TODO: Clean up \u00a0 and other nbsp; issues
        event_location = page.xpath('//div[contains(@class,"MeetingAddress")]/text()')[0].strip()

        event_name = '{} {}'.format(event_group, event_type)

        event_date_str = page.xpath('//span[@id="ContentPlaceholder1_lblMeetingDate"]/text()')[0].strip()
        # 3/25/2020 6:00 PM
        event_date = datetime.datetime.strptime(event_date_str, '%m/%d/%Y %I:%M %p')
        event_date = self.TIMEZONE.localize(event_date)

        event = Event(name=event_name,
            start_date=event_date,
            # description=description,
            location_name=event_location,
            )
        event.add_source(url)

        for link_row in page.xpath('//div[@id="ContentPlaceholder1_pnlDownloads"]/a[not(@onclick)]'):
            link_href = link_row.xpath('@href')[0]
            link_text = link_row.xpath('text()')[0].strip()
            event.add_document(
                link_text,
                link_href,
                on_duplicate='ignore'
            )

        # TODO: ones with onlicks are video links

        yield event