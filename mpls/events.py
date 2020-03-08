from pupa.scrape import Scraper
from pupa.scrape import Event
import datetime
import json
import lxml
import requests
import pprint
import pytz

class MplsEventScraper(Scraper):
    TIMEZONE = pytz.timezone("America/Chicago")

    def scrape(self):
        cal_url = 'https://lims.minneapolismn.gov/Calendar/GetCalenderList?fromDate=Jan%201,%202020&toDate=Dec%201,%202020&meetingType=1&committeeId=null&pageCount=1000&offsetStart=0&abbreviation=undefined&keywords='
        req = self.get(cal_url)
        rows = json.loads(req.content)

        for row in rows:
            yield from self.scrape_row(row)

    def scrape_row(self, row):
        # pprint.pprint(row)
        event_title = row['CommitteeName']
        event_date = datetime.datetime.strptime(row['MeetingTime'], '%Y-%m-%dT%H:%M:%S')
        event_date = self.TIMEZONE.localize(event_date)
        event_location = '{}, {}'.format(row['Location'], row['Address'])

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
            # description=event_subtitle,
            location_name=event_location,
            status=status
        )

        # IE https://lims.minneapolismn.gov/MarkedAgenda/Charter/1370
        if row['AgendaId'] != 0:
            agenda_url = 'https://lims.minneapolismn.gov/MarkedAgenda/{}/{}'
            print(agenda_url.format(row['Abbreviation'], row['AgendaId']))
            event.add_document('agenda', agenda_url.format(row['Abbreviation'], row['AgendaId']))

        event.add_source('https://lims.minneapolismn.gov/Calendar/citycouncil/weekly')
        yield event
