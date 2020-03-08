import datetime
import pytz
import lxml
import json
import re

from lxml import html

from pupa.scrape import Scraper
from pupa.scrape import Event

class BostonEventScraper(Scraper):
    BASE_URL = "https://www.boston.gov/public-notices"
    TIMEZONE = pytz.timezone("America/New_York")
    UTC = pytz.timezone("UTC")


    def scrape(self, window=3):
        n_days_ago = datetime.datetime.utcnow() - datetime.timedelta(float(window))

        req = self.get(self.BASE_URL)
        page = lxml.html.fromstring(req.content)

        last_url = page.xpath('//a[@title="Go to last page"]/@href')[0]
        last_page = int(re.findall(r'page=(\d+)', last_url)[0])

        for page_num in range(0, last_page+1):
            yield from self.scrape_page(page_num)


    def scrape_page(self, page):
        list_url = '{}?title=&page={}'.format(self.BASE_URL, page)

        req = self.get(list_url)
        page = lxml.html.fromstring(req.content)
        page.make_links_absolute(self.BASE_URL)

        for row in page.xpath('//div[contains(@class,"b-c")]/div[contains(@class,"g ")]'):
            event_url = row.xpath('div/div/a/@href')[0]
            yield from self.scrape_event(event_url)


    def scrape_event(self, url):
        req = self.get(url)
        page = lxml.html.fromstring(req.content)
        page.make_links_absolute(self.BASE_URL)

        # info_box = page.xpath('//div[contains(@class,"department-info-wrapper")]/div[contains(@class,"column")]')[0]

        event_date = page.xpath('//div[contains(@class,"event-date")]/time/@datetime')[0]
        event_date = datetime.datetime.fromisoformat(event_date.replace('Z',''))
        event_date = self.UTC.localize(event_date)

        event_title = page.xpath('string(//div[contains(@class,"department-info-wrapper")]/div[contains(@class,"column")]/h1/h1)').strip()

        event_subtitle = page.xpath('string(//div[contains(@class,"department-info-wrapper")]/div[contains(@class,"column")]/div[contains(@class,"intro-text")])').strip()

        json_ld = page.xpath('//script[@type="application/ld+json"]/text()')[0]
        json_ld = json.loads(json_ld)

        address = json_ld['@graph'][1]['location']['address']
        event_location = '{}, {} {} {}'.format(
            address['streetAddress'],
            address['addressLocality'],
            address['addressRegion'],
            address['postalCode'],
        )

        # {'enum': ['cancelled', 'tentative', 'confirmed', 'passed'],
        if 'cancelled' in event_title.lower():
            status = 'cancelled'
        elif event_date < self.TIMEZONE.localize(datetime.datetime.today()):
            status = 'passed'
        else:
            status = 'tentative'

        event = Event(
            name=event_title,
            start_date=event_date,
            description=event_subtitle,
            location_name=event_location,
            status=status
        )

        event.add_source(url)

        for docket in page.xpath('//div[@class="body"]/ol/li'):
            agenda_text = docket.xpath('string(.)').strip()
            agenda_text = re.sub(r'\s+',' ', agenda_text)
            event.add_agenda_item(agenda_text)

        for link in page.xpath('//div[div/div[contains(text(),"Resources")]]//a'):
            link_url = link.xpath('@href')[0]
            link_text = link.xpath('string(.)').strip()
            event.add_document(link_text, link_url, on_duplicate="ignore")
        yield event