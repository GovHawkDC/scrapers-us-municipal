import datetime
import re

import pprint
import pytz
import requests
from legistar.events import LegistarEventsScraper
from pupa.scrape import Event, Scraper

class {{ class_name }}EventScraper(LegistarEventsScraper, Scraper):
    BASE_URL = 'http://webapi.legistar.com/v1/{{city_id}}'
    WEB_URL = "https://{{city_id}}.legistar.com/"
    EVENTSPAGE = "https://{{city_id}}.legistar.com/Calendar.aspx"    
    TIMEZONE = "{{ timezone }}"

    def scrape(self, window=3):
        n_days_ago = datetime.datetime.utcnow() - datetime.timedelta(float(window))

        for web_event in self.events(n_days_ago):
            # pprint.pprint(web_event)
            yield web_event



            when = api_event['start']
            location = api_event[u'EventLocation']

            extracts = self._parse_comment(api_event[u'EventComment'])
            description, room, status, invalid_event = extracts

            if invalid_event:
                continue

            if room:
                location = room + ', ' + location

            if not status:
                status = api_event['status']
                

            if description :
                e = Event(name=api_event["EventBodyName"],
                          start_date=when,
                          description=description,
                          location_name=location,
                          status=status)
            else :
                e = Event(name=api_event["EventBodyName"],
                          start_date=when,
                          location_name=location,
                          status=status)

            e.pupa_id = str(api_event['EventId'])

            if web_event['Meeting video'] != 'Not\xa0available' :
                e.add_media_link(note='Recording',
                                 url = web_event['Meeting video']['url'],
                                 type="recording",
                                 media_type = 'text/html')
            
            if 'Published agenda' in web_event:
                self.addDocs(e, web_event, 'Published agenda')
            if 'Notice' in web_event:
                self.addDocs(e, web_event, 'Notice')
            if 'Published summary' in web_event:
                self.addDocs(e, web_event, 'Published summary')
            if 'Captions' in web_event:
                self.addDocs(e, web_event, 'Captions')

            participant = api_event["EventBodyName"]

            e.add_participant(name=participant,
                              type="organization")

            for item in self.agenda(api_event):
                agenda_item = e.add_agenda_item(item["EventItemTitle"])
                if item["EventItemMatterFile"]:
                    identifier = item["EventItemMatterFile"]
                    agenda_item.add_bill(identifier)

            participants = set()
            for call in self.rollcalls(api_event):
                if call['RollCallValueName'] == 'Present':
                    participants.add(call['RollCallPersonName'])

            for person in participants:
                e.add_participant(name=person,
                                  type="person")

            e.add_source(self.BASE_URL + '/events/{EventId}'.format(**api_event), 
                         note='api')

            if 'url' in web_event['Meeting Name']:
                e.add_source(web_event['Meeting Name']['url'], note='web')
            elif 'url' in web_event['Meeting Details']:
                e.add_source(web_event['Meeting Details']['url'], note='web')

            yield e            