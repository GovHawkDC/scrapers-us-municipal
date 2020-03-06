from pupa.scrape import Event, VoteEvent, Scraper
from pupa.utils import _make_pseudo_id
import datetime
import itertools
import pytz
import requests
import re
import lxml.html


class AgendaCenterScraper():
    BASE_URL = ""
    TIMEZONE = ""
    s = requests.Session()

    def session(self, action_date):
        return str(action_date.year)

    def scrape(self, window=3):
        year = datetime.datetime.today().year
        search_url = '{}/Search/'.format(self.BASE_URL)
        params = {
            'term': '',
            'CIDs': 'all',
            'startDate': '01/01/{}'.format(year),
            'endDate': '12/31/{}'.format(year),
            'dateRange': '',
            'dateSelector': '',
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/79.0.3945.117 Safari/537.36",
            "referer": self.BASE_URL,
            "Sec-Fetch-Mode": "navigate",
        }


        req = self.s.get(search_url, params=params, headers=headers)
        req.raise_for_status()
        html = req.text

        page = lxml.html.fromstring(html)
        page.make_links_absolute(self.BASE_URL)

        # agencies
        for row in page.xpath('//div[contains(@class, "listing")]'):
            # it's typod as expandCollaspseCategory which seems like something they might fix, hence the OR
            agency_name = row.xpath('h2[contains(@onclick, "expandCollaspseHeader") or contains(@onclick, "expandCollapseHeader")]/text()')[0].strip()
            agency_name = agency_name.replace('Agendas', '').strip()
        
            print(agency_name)
            # event_date = row.xpath('div[contains(@class, "RowTop")]/div[contains(@class, "RowLink")]/a/text()')[0].strip()
            # event_url = row.xpath('div[contains(@class, "RowTop")]/div[contains(@class, "RowLink")]/a/@href')[0].strip()

            for event_row in row.xpath('.//table/tbody/tr'):
                yield from self.scrape_event_page(agency_name, event_row)

    def scrape_event_page(self, agency_name, row):


        event_location = 'Not provided'
        event_name = '{} Meeting'.format(agency_name)

        # Jul 18 2019
        event_date_str = row.xpath('string(td/h4/a/strong)').strip()
        event_date = datetime.datetime.strptime(event_date_str, '%b %d, %Y')
        event_date = self.TIMEZONE.localize(event_date)

        description = row.xpath('td/p/text()')[0].strip()

        event = Event(name=event_name,
            start_date=event_date,
            description=description,
            location_name=event_location,
            )
        event.add_source(self.BASE_URL)

        print(event_name, event_date, description, event_location)

        # participant = "{} {}".format(self.JURIS_NAME, event_group)
        # event.add_participant(participant, 'organization')

        # for link_row in page.xpath('//div[@id="ContentPlaceholder1_pnlDownloads"]/a[not(@onclick)]'):
        #     link_href = link_row.xpath('@href')[0]
        #     link_text = link_row.xpath('text()')[0].strip()
        #     event.add_document(
        #         link_text,
        #         link_href,
        #         on_duplicate='ignore'
        #     )

        # # TODO: ones with onlicks are video links

        # for outline_row in page.xpath('//span[@id="ContentPlaceholder1_lblOutline"]/table[@id="MeetingDetail"]/tr'):
        #     item_title = outline_row.xpath('string(td[contains(@class,"Title")])').strip()

        #     if outline_row.xpath('td[contains(@class,"Num")]/text()'):
        #         item_num = outline_row.xpath('td[contains(@class,"Num")]/text()')[0].strip()
        #         item_title = '{} {}'.format(item_num, item_title)
        #         # TODO: Should we add links here as documents? Might overwhelm
        #     event.add_agenda_item(item_title)

        yield event