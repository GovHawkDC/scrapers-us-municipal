from pupa.scrape import Scraper
from pupa.scrape import Event
import requests
import datetime
import lxml
import pytz
from lxml import html

class HonoluluEventScraper(Scraper):
    TIMEZONE = pytz.timezone("Pacific/Honolulu")

    def scrape(self):
        url = 'http://www.honolulu.gov/council-cal/search.form/2018/03/13/-.html'

        html = self.get(url)
        page = lxml.html.fromstring(html.content)

        for row in page.xpath('//table[@title="calendar"]/tbody/tr'):
            event_title = row.xpath('td[1]/a/text()')[0].strip()
            event_date = '{} {}'.format(row.xpath('td[3]/text()')[0].strip(), row.xpath('td[4]/text()')[0].strip())
            # Thu 03-16-2017 	09:00 AM
            event_date = datetime.datetime.strptime(event_date, '%a  %m-%d-%Y %I:%M %p')
            event_date = self.TIMEZONE.localize(event_date)

            event_location = row.xpath('string(td[5])').strip()
            if event_location == '':
                event_location = 'Not Provided'

            # {'enum': ['cancelled', 'tentative', 'confirmed', 'passed'],
            if 'cancelled' in event_title.lower() or 'cancelled' in row.xpath('string(td[6])'):
                status = 'cancelled'
            elif event_date < self.TIMEZONE.localize(datetime.datetime.today()):
                status = 'passed'
            else:
                status = 'tentative'

            event = Event(
                name=event_title,
                start_date=event_date,
                # description=event_subtitle,
                location_name=event_location,
                status=status
            )

            if row.xpath('td[6]/a'):
                for link in row.xpath('td[6]/a[@href != ""]'):
                    link_url = link.xpath('@href')[0]
                    link_text = link.xpath('text()')[0].strip()
                    event.add_document(link_text, link_url, on_duplicate='ignore')

            event.add_source('http://www.honolulu.gov/council-cal')
            yield event
