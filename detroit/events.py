import datetime
import json
import lxml.html
import pytz
import re
from pupa.scrape import Scraper
from pupa.scrape import Event


class DetroitEventScraper(Scraper):
    TIMEZONE = pytz.timezone('America/Detroit')
    last_page = 1

    def scrape(self):

        url = 'https://detroitmi.gov/Calendar-and-Events?field_start_value=%2B0%20day&title=&term_node_tid_depth=All&term_node_tid_depth_1=All&term_node_tid_depth_2=All&page={}'
        # needs to be implemented
        yield from self.scrape_calendar_page(0)

        if self.last_page > 0:
            for i in range(1, self.last_page):
                yield from self.scrape_calendar_page(i)
        pass

    def scrape_calendar_page(self, page_num):
        url = 'https://detroitmi.gov/Calendar-and-Events?field_start_value=%2B0%20day&title=&term_node_tid_depth=All&term_node_tid_depth_1=All&term_node_tid_depth_2=All&page={}'
        page_url = url.format(page_num)

        page = self.get(page_url).content
        page = lxml.html.fromstring(page)
        page.make_links_absolute(page_url)


        if page_num == 0:
            last_link = page.xpath('//a[@rel="last"]/@href')[0]
            self.last_page = int(last_link[-1])
        
        # '//div[section[contains(@class,"event-preview-top")]]'
        for row in page.xpath('//div[section[contains(@class,"event-preview-top")]]'):
            event_url = row.xpath('.//article[contains(@class,"article-title")]/h3/a/@href')[0]
            yield from self.scrape_event_page(event_url)
    
    def scrape_event_page(self, url):
        page = self.get(url).content
        page = lxml.html.fromstring(page)
        page.make_links_absolute(url)

        if page.xpath('//article[contains(@class,"time")]/time'):
            # note that the time tag in the date has the wrong hour,
            # but the time tag under the time has the right date and hour
            time = page.xpath('//article[@class="time"]/time/@datetime')[0]

            event_date = pytz.utc.localize(
                datetime.datetime.strptime(time, '%Y-%m-%dT%H:%M:%SZ')
            )
        else:
            # no machine readable time, combine date / time fields
            # right date, wrong time
            date = page.xpath('//article[contains(@class,"date")]/time/@datetime')[0]
            date = date.split('T')[0]
            # just the time
            time = page.xpath('string(//article[@class="time"])').strip()
            event_date = pytz.utc.localize(
                datetime.datetime.strptime(
                    '{} {}'.format(date, time),
                    '%Y-%m-%d %I:%M %p'
                )
            )


        event_name = page.xpath('//h1[contains(@class,"page-header")]/span/text()')[0]

        event_loc = "See Description"

        if page.xpath('//article[contains(@class,"location-info")]'):
            event_loc = page.xpath('string(//article[contains(@class,"location-info")])').strip()

        event_desc=""

        if page.xpath('//article[contains(@class,"description")]'):
            event_desc = page.xpath('string(//article[contains(@class,"description")])').strip()

        event = Event(
            name=event_name,
            start_date=event_date,
            description=event_desc,
            location_name=event_loc,
        )

        for file_link in page.xpath('//span[contains(@class,"file-link")]/a'):
            file_url = file_link.xpath('@href')[0]
            file_title = file_link.xpath('text()')[0].strip()

            # ex: application/pdf; length=674097
            file_meta = file_link.xpath('@type')[0]
            file_mime = file_meta.split(';')[0]

            event.add_document(
                file_title,
                file_url,
                media_type=file_mime,
                on_duplicate='ignore'
            )

        event.add_source(url)

        yield event