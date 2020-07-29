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
        url = "https://www.nashville.gov/News-Media/Calendar-of-Events.aspx"
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

            print(doc_url, doc_title)
            event.add_document(doc_title, doc_url)

        yield event
