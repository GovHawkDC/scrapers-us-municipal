import datetime
import lxml.html
import pytz
import re
from pupa.scrape import Scraper
from pupa.scrape import Event


class KcmoEventScraper(Scraper):
    TIMEZONE = pytz.timezone("America/Chicago")

    def scrape(self):
        yield from self.scrape_upcoming()
        yield from self.scrape_old_meetings()

    def scrape_old_meetings(self):
        url = 'http://cityclerk.kcmo.org/LiveWeb/Meetings/HistoricalMeetings.aspx?t=c'
        page = self.get(url).content
        page = lxml.html.fromstring(page)
        page.make_links_absolute(url)

        for row in page.xpath('//table[contains(@id, "ContentPlaceHolder1_dg")]' \
            '/tr[contains(@class,"outputRow") or contains(@class,"altOutputRow")]'):
            date_col = row.xpath('td[1]/text()')[0].strip()
            name_col = row.xpath('td[2]/a/text()')[0].strip()
            time_col = row.xpath('td[3]/text()')[0].strip()
            agenda_link = row.xpath('td[5]/a')
            minutes_link = row.xpath('td[6]/a')

            event_date = '{} {}'.format(date_col, time_col)
            event_start = self.TIMEZONE.localize(
                datetime.datetime.strptime(event_date, "%m/%d/%Y %I:%M %p")
            )

            event = Event(
                name=name_col,
                start_date=event_start,
                description='',
                location_name='See Description'
            )

            event.add_source(url)

            if agenda_link:
                event.add_document(
                    'Agenda',
                    agenda_link[0].xpath('@href')[0]
                )

            if minutes_link:
                event.add_document(
                    'Minutes',
                    minutes_link[0].xpath('@href')[0]
                )

            yield event

    def scrape_upcoming(self):
        url = 'http://cityclerk.kcmo.org/LiveWeb/Meetings/PublicNotices.aspx'
        page = self.get(url).content
        page = lxml.html.fromstring(page)
        page.make_links_absolute(url)

        for row in page.xpath('//table[contains(@id, "ContentPlaceHolder1_dg")]' \
            '/tr[contains(@class,"outputRow") or contains(@class,"altOutputRow")]'):

            name_col = row.xpath('td[2]/a/text()')[0].strip()
            date_col = row.xpath('td[3]/text()')[0].strip()
            agenda_link = row.xpath('td[5]/a')

            event_start = self.TIMEZONE.localize(
                datetime.datetime.strptime(date_col, "%m/%d/%Y %I:%M %p")
            )

            event = Event(
                name=name_col,
                start_date=event_start,
                description='',
                location_name='See Description'
            )

            if agenda_link:
                event.add_document(
                    'Agenda',
                    agenda_link[0].xpath('@href')[0]
                )

            event.add_source(url)

            yield event
