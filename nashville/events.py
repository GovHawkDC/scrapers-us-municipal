import datetime
import lxml.html
import pytz
import re
from pupa.scrape import Scraper
from pupa.scrape import Event


class NashvilleEventScraper(Scraper):
    TIMEZONE = pytz.timezone('America/Chicago')
    agendas = {}
    minutes = {}

    def scrape(self):
        url = 'https://www.nashville.gov/News-Media/Calendar-of-Events.aspx'
        page = self.get(url).content
        page = lxml.html.fromstring(page)
        page.make_links_absolute(url)

        for row in page.xpath('//tr[contains(@class,"rgRow") or contains(@class,"rgAltRow")]'):
            yield from self.scrape_event_page(row.xpath('td[2]/a/@href')[0])

    def scrape_event_page(self, url):
        # https://www.nashville.gov/News-Media/Calendar-of-Events/Event-Details/ID/12007/begin/8-4-2020/Metropolitan-Council-Meeting.aspx
        page = self.get(url).content
        page = lxml.html.fromstring(page)
        page.make_links_absolute(url)

        event_title = page.xpath('//h1/text()')[0].strip()

        # we can use the google cal link to get nice clean start and end times
        gcal_link = page.xpath('//div[@class="addtocal-wrap"]/div/ul/li/a[contains(@id, "hlGoogleCalendar")]/@href')[0]
        print(gcal_link)

        dates = re.search(r'&dates=(.*?)&', gcal_link).group(1)
        dates = dates.split('/')

        print(dates)

        event_start = self.TIMEZONE.localize(
            datetime.datetime.strptime(
                dates[0],
                '%Y%m%dT%H%M%SZ'
            )
        )

        event_end = self.TIMEZONE.localize(
            datetime.datetime.strptime(
                dates[1],
                '%Y%m%dT%H%M%SZ'
            )
        )

        event_desc = ''

        event_loc = 'TBD'

        # regex of &dates=(.*)& to snag those dates
        # then split on / and parse it up

        event = Event(
            name=event_title,
            start_date=event_start,
            end_date=event_end,
            description=event_desc,
            location_name=event_loc,
        )

        event.add_source(url)

        yield event
