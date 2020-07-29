import datetime
import lxml.html
import pytz
import re
from pupa.scrape import Scraper
from pupa.scrape import Event


class NashvilleEventScraper(Scraper):
    TIMEZONE = pytz.timezone("America/Chicago")
    agendas = {}
    minutes = {}

    def scrape(self):
        agenda_url = 'https://www.nashville.gov/Metro-Clerk/Legislative/Agendas.aspx'
        self.agendas = self.scrape_file_list(agenda_url)

        minutes_url = 'https://www.nashville.gov/Metro-Clerk/Legislative/Minutes.aspx'
        self.minutes = self.scrape_file_list(minutes_url)

        today = datetime.date.today()
        
        fwd_one_month = today + datetime.timedelta(30)
        back_one_week = today - datetime.timedelta(7)

        fwd_one_month = fwd_one_month.strftime('%m-%d-%Y')
        back_one_week = back_one_week.strftime('%m-%d-%Y')

        url = "https://www.nashville.gov/News-Media/Calendar-of-Events.aspx?sdate={}&edate={}"
        url = url.format(back_one_week, fwd_one_month)
        page = self.get(url).content
        page = lxml.html.fromstring(page)
        page.make_links_absolute(url)

        for row in page.xpath(
            '//tr[contains(@class,"rgRow") or contains(@class,"rgAltRow")]'
        ):
            yield from self.scrape_event_page(row.xpath("td[2]/a/@href")[0])

    def scrape_event_page(self, url):
        # https://www.nashville.gov/News-Media/Calendar-of-Events/Event-Details/ID/12007/begin/8-4-2020/Metropolitan-Council-Meeting.aspx
        page = self.get(url).content
        page = lxml.html.fromstring(page)
        page.make_links_absolute(url)

        event_title = page.xpath("//h1/text()")[0].strip()

        # we can use the google cal link to get nice clean start and end times
        gcal_link = page.xpath(
            '//div[@class="addtocal-wrap"]/div/ul/li/a[contains(@id, "hlGoogleCalendar")]/@href'
        )[0]

        dates = re.search(r"&dates=(.*?)&", gcal_link).group(1)
        dates = dates.split("/")

        event_start = self.TIMEZONE.localize(
            datetime.datetime.strptime(dates[0], "%Y%m%dT%H%M%SZ")
        )

        event_end = self.TIMEZONE.localize(
            datetime.datetime.strptime(dates[1], "%Y%m%dT%H%M%SZ")
        )

        event_desc = ""

        if page.xpath('//div[contains(@id, "EventDetails_pnlEvent")]/p/text()'):
            event_desc = "\n".join(
                page.xpath('//div[contains(@id, "EventDetails_pnlEvent")]/p/text()')[1:]
            )
            event_desc = event_desc.strip()

        event_loc = "See Description"

        if page.xpath('//div[contains(@id, "EventDetails_pnlLocation")]'):
            event_loc = "\n".join(
                page.xpath(
                    '//div[contains(@id, "EventDetails_pnlLocation")]/p[1]/text()'
                )
            )

        event = Event(
            name=event_title,
            start_date=event_start,
            end_date=event_end,
            description=event_desc,
            location_name=event_loc,
        )

        event.add_source(url)

        for doc_link in page.xpath(
            '//div[contains(@id, "EventDetails_pnlEvent")]'
            '//a[contains(@href,"document")]'
        ):
            doc_url = doc_link.xpath("@href")[0]
            doc_title = doc_link.xpath("text()")[0].strip()

            event.add_document(doc_title, doc_url, on_duplicate='ignore')

        if 'metropolitan council meeting' in event_title.lower():
            date_key = event_start.strftime('%Y%m%d')
            if date_key in self.agendas:
                event.add_document(
                    'Agenda',
                    self.agendas[date_key],
                    on_duplicate="ignore"
                )
            if date_key in self.minutes:
                event.add_document(
                    'Minutes',
                    self.minutes[date_key],
                    on_duplicate="ignore"
                )

        yield event

    # agendas as minutes aren't always linked from the event pages
    # so scrape them first and save them in a mapping of YYYYMMDD => url
    def scrape_file_list(self, url):
        retVal = {}

        page = self.get(url).content
        page = lxml.html.fromstring(page)
        page.make_links_absolute(url)
        
        for row in page.xpath('//div[contains(@class,"ShowFilesColumn")]/ul/li/a'):
            link_url = row.xpath('@href')[0]
            link_text = row.xpath('text()')[0]
            # extract just the date, they've got some funky extras sometimes
            link_text = re.findall(r'\w+\s+\d+,\s+\d{4}', link_text, re.IGNORECASE)[0]
            link_date = datetime.datetime.strptime(link_text, '%B %d, %Y')
            link_key = link_date.strftime('%Y%m%d')
            retVal[link_key] = link_url
        return retVal