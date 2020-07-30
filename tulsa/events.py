import datetime
import lxml.html
import pytz
import re
from pupa.scrape import Scraper
from pupa.scrape import Event


class TulsaEventScraper(Scraper):
    TIMEZONE = pytz.timezone("America/Chicago")

    def scrape(self):
        url = 'http://legacy.tulsacouncil.org/inc/search/meeting_list.php'

        year = datetime.datetime.today().year
        for month_num in range(1,13):
            args = {
                'Submit': 'Go',
                'MeetingMonth': str(month_num),
                'MeetingYear': str(year)
            }

            page = self.post(url, args).content
            page = lxml.html.fromstring(page)
            page.make_links_absolute(url)

            for row in page.xpath('//td[a]'):
                print(row.xpath('string(.)'))
                event_time_str = row.xpath('text()')[0].strip()

                event_date =  re.search(r"\d+\/\d+\/\d+\s+\d+:\d+\s+\w+", event_time_str).group(0)
                event_start = self.TIMEZONE.localize(
                    datetime.datetime.strptime(event_date, "%m/%d/%Y %I:%M %p")
                )

                event_link = row.xpath('a/@href')[0]
                event_title = row.xpath('a/text()')[0].strip()

                event_desc = 'See Agenda'
                event_loc = 'See Agenda'

                print(event_title, event_time_str, event_title)

                event = Event(
                    name=event_title,
                    start_date=event_start,
                    description=event_desc,
                    location_name=event_loc,
                )

                event.add_source(event_link)

                event.add_document(
                    'Agenda',
                    event_link
                )

                yield event