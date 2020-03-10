from pupa.scrape import Scraper
from pupa.scrape import Event
import requests
import datetime
import lxml
import pytz
from lxml import html


class DesmoinesEventScraper(Scraper):
    TIMEZONE = pytz.timezone("America/Chicago")

    def scrape(self):
        url = 'https://www.dsm.city/government/council_meetings_and_agendas/index.php'

        html = self.get(url)
        page = lxml.html.fromstring(html.content)

        for row in page.xpath('//table[contains(@class,"table")]/tbody/tr'):
            # print(row.xpath('string(.)'))
            event_title = row.xpath('th[1]/text()')[0].strip()
            if row.xpath('th[1]/time'):
                event_date = row.xpath('th[1]/time/text()')[0].strip()
            else:
                event_date = row.xpath('th[1]/text()')[0].strip()[0:8]
            event_date = '{} 16:30'.format(event_date)
            # 01/27/20
            event_date = datetime.datetime.strptime(event_date, '%m/%d/%y %H:%M')
            event_date = self.TIMEZONE.localize(event_date)

            event_location = 'City Hall, Council Chambers, 400 Robert D. Ray Drive, 2nd Floor, Des Moines, IA 50309'

            # {'enum': ['cancelled', 'tentative', 'confirmed', 'passed'],
            if 'cancelled' in event_title.lower():
                status = 'cancelled'
            elif event_date < self.TIMEZONE.localize(datetime.datetime.today()):
                status = 'passed'
            else:
                status = 'tentative'

            event_title = event_title[9:].strip()

            print(event_title, event_date, event_location)
            
            event = Event(
                name=event_title.strip(),
                start_date=event_date,
                location_name=event_location,
                status=status
            )

            event.add_source(url)
            yield event