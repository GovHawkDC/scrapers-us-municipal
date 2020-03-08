import datetime
import pytz
import lxml
import json

from lxml import html

from pupa.scrape import Scraper
from pupa.scrape import Event

class BostonEventScraper(Scraper):
    BASE_URL = "https://www.boston.gov/public-notices"
    TIMEZONE = pytz.timezone("America/New_York")


    def scrape(self, window=3):
        n_days_ago = datetime.datetime.utcnow() - datetime.timedelta(float(window))
        yield from self.scrape_page(1)


    def scrape_page(self, page):
        list_url = '{}?title=&page={}'.format(self.BASE_URL, page)

        req = self.get(list_url)
        page = lxml.html.fromstring(req.content)
        page.make_links_absolute(self.BASE_URL)

        for row in page.xpath('//div[contains(@class,"b-c")]/div[contains(@class,"g ")]'):
            event_url = row.xpath('div/div/a/@href')[0]
            print(event_url)
            yield from self.scrape_event(event_url)


    def scrape_event(self, url):
        req = self.get(url)
        page = lxml.html.fromstring(req.content)

        # info_box = page.xpath('//div[contains(@class,"department-info-wrapper")]/div[contains(@class,"column")]')[0]

        event_date = page.xpath('//div[contains(@class,"event-date")]/time/@datetime')[0]
        event_date = datetime.datetime.fromisoformat(event_date.replace('Z',''))

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
        print(event_location)

        print(event_date, event_title, event_subtitle, event_location)
        yield {}
            #     e = Event(name=api_event["EventBodyName"],
            #               start_date=when,
            #               description=description,
            #               location_name=location,
     

            #     e.add_media_link(note='Recording',
            #                      url = web_event['Meeting video']['url'],
            #                      type="recording",
   
            # e.add_participant(name=participant,
            #                   type="organization")

            # for item in self.agenda(api_event):
            #     agenda_item = e.add_agenda_item(item["EventItemTitle"])
            #     if item["EventItemMatterFile"]:
            #         identifier = item["EventItemMatterFile"]
            #         agenda_item.add_bill(identifier)


            # e.add_source(web_event['Meeting Name']['url'], note='web')

            # yield e