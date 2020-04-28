from pupa.scrape import Scraper
from pupa.scrape import Event
import json
import datetime
import lxml
import pprint
import pytz

class MinneapolisEventScraper(Scraper):
    TIMEZONE = pytz.timezone('America/Chicago')
    AGENDA_URL = 'https://lims.minneapolismn.gov/MarkedAgenda/{com_abbr}/{id}'

    def scrape(self, start_date=None, end_date=None):
        # needs to be implemented
        # https://lims.minneapolismn.gov/Calendar/GetCalenderList?fromDate=Mar%2029,%202020&toDate=May%203,%202020&meetingType=2&committeeId=null&pageCount=1000&offsetStart=0&abbreviation=undefined&keywords=
        events_url = "https://lims.minneapolismn.gov/Calendar/GetCalenderList?fromDate=Jan%2001,%202020&toDate=May%203,%202020&meetingType=1&committeeId=null&pageCount=1000&offsetStart=0&abbreviation=undefined&keywords="
        req = self.get(events_url)
        rows = json.loads(req.content)
        for row in rows:
            yield from self.scrape_event(row)

    def scrape_event(self, row):
        location = row['Address']

        if not location:
            location = 'Not Provided'

        # 2020-04-29T13:30:00
        event_date_str = row['MeetingTime']
        event_date = datetime.datetime.strptime(event_date_str, "%Y-%m-%dT%H:%M:%S")
        event_date = self.TIMEZONE.localize(event_date)

        description = str(row['Description'])

        status = ''
        if event_date > self.TIMEZONE.localize(datetime.datetime.today()):
            status = 'tentative'
        else:
            status = 'passed'

        if 'cancellation' in description.lower() or 'cancelled' in description.lower():
            status = 'cancelled'

        event = Event(
            name=row['CommitteeName'],
            start_date=event_date,
            location_name=location,
            status=status,
        )

        if row['CommitteeName']:
            event.add_participant(name=row['CommitteeName'],
                    type="organization")

        if row['MarkedAgendaPublished']:
            agenda_url = self.AGENDA_URL.format(com_abbr=row['Abbreviation'], id=row['AgendaId'])
            print(agenda_url)

        event.add_source('https://lims.minneapolismn.gov/Calendar/all/monthly')
        print( event)
        yield event
