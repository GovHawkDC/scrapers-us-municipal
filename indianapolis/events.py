import datetime
import json
import pytz
import re
from lxml import etree, html
from pupa.scrape import Scraper
from pupa.scrape import Event


class IndianapolisEventScraper(Scraper):
    TIMEZONE = pytz.timezone('America/Indiana/Indianapolis')
    agendas = {}
    minutes = {}

    def scrape(self):
        # http://calendar.indy.gov/Eventlist.aspx?fromdate=7/1/2020&todate=8/31/2020
        # &display=Month&view=Grid&type=public&download=download&dlType=XML
        self.get_agendas_and_minutes()

        today = datetime.date.today()
        
        three_months = today + datetime.timedelta(3 * 30)
        back_three_months = today - datetime.timedelta(3 * 30)

        today = today.strftime('%m/%d/%Y')
        back_three_months = back_three_months.strftime('%m/%d/%Y')
        three_months = three_months.strftime('%m/%d/%Y')

        url = 'http://calendar.indy.gov/Eventlist.aspx?fromdate={}&todate={}' \
            '&display=Month&' \
            'view=Grid&type=public&download=download&dlType=XML'
        url = url.format(back_three_months, three_months)
        page = self.get(url).content
        page = etree.fromstring(page)

        for row in page.xpath('//Event'):
            event_name = row.xpath('string(EventName)')
            event_desc = row.xpath('string(EventDescription)')

            event_loc = "See Description"

            event_start = self.parse_date_fields(
                row.xpath('string(StartDate)'),
                row.xpath('string(StartTime)')
            )

            event_end = self.parse_date_fields(
                row.xpath('string(EndDate)'),
                row.xpath('string(EndTime)')
            )

            event = Event(
                name=event_name,
                start_date=event_start,
                end_date=event_end,
                description=event_desc,
                location_name=event_loc,
            )

            contact = row.xpath('string(ContactName)')
            if contact != '':
                event.add_person(
                    name=contact,
                    note="Contact"
                )

            event.add_source('http://calendar.indy.gov/')
            yield event

    def parse_date_fields(self, day, time):
        if time != '':
            full_date = '{} {}'.format(day, time)
            return self.TIMEZONE.localize(
                datetime.datetime.strptime(full_date, "%m/%d/%Y %I:%M %p")
            )
        else:
            return self.TIMEZONE.localize(
                datetime.datetime.strptime(day, "%m/%d/%Y")
            )

    def get_agendas_and_minutes(self):
        # agendas and minutes are pdfs linked to in markdown,
        # which is freeform text saved as a field in a json document
        #
        # sweet.
        url = 'https://www.indy.gov/api/v1/activity_page/fad6791b-7718-4bf3-b5fd-81e4cefc57ab'
        page = self.get(url).content
        page = json.loads(page)

        agendas = page['activity']['description']

        # - month day, year: [Agenda](url)
        agenda_link_regex = r'-\s+(?P<month>\w+)\s+(?P<day>\d+)[,]*\s+(?P<year>\d+):\s+\[\w+\]\((?P<url>[\w\d\.\:\/\-]+)\)'
 
        self.agendas = self.parse_markdown_field(page['activity']['description'], agenda_link_regex)
       
        for related in page['related_activities']:
            if 'Council Meeting Minutes' in related['title']:
                print("RUNNING MINUTES PARSER")
                # - [Month Day, Year](url)
                minutes_regex = r'-\s*\[(?P<month>\w+)\s+(?P<day>\d+)[,]*\s+(?P<year>\d+)\]\((?P<url>[\w\d\.\:\/\-]+)\)'
                self.minutes = self.parse_markdown_field(related['description'], minutes_regex)

    def parse_markdown_field(self, markdown, link_regex):
        retVal = {}

        # add a whole markdown library dependency? Nah.
        # this is coming from some sort of backend so seems to be consistent
        matches = re.findall(link_regex, markdown, re.MULTILINE)

        for match in matches:
            # print(match)
            date_str = '{}-{}-{}'.format(
                match[0],
                match[1],
                match[2]
            )
            agenda_date = datetime.datetime.strptime(date_str, '%B-%d-%Y').strftime('%Y-%m-%d')
            # retVal['2019-01-07'] = https://citybase-cms-prod.s3.amazonaws.com/b4dad5aa8b2647c39309da3ec5d26f7f.pdf
            retVal[agenda_date] = match[3]

        return retVal
