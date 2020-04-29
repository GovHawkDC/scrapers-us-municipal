from pupa.scrape import Scraper
from pupa.scrape import Event
import json
import datetime as dt
import lxml.html
import pprint
import pytz


class MinneapolisEventScraper(Scraper):
    TIMEZONE = pytz.timezone("America/Chicago")
    AGENDA_URL = "https://lims.minneapolismn.gov/MarkedAgenda/{com_abbr}/{id}"

    def scrape(self, start_date=None, end_date=None):

        if start_date is None:
            start_date = dt.datetime.today() - dt.timedelta(days=30)
            end_date = dt.datetime.today() + dt.timedelta(days=30)
        else:
            start_date = dt.datetime.strptime(start_date,"%Y-%m-%d")
            end_date = dt.datetime.strptime(end_date,"%Y-%m-%d")

        date_input_format = "%b %d, %Y"

        events_url = (
            "https://lims.minneapolismn.gov/Calendar/GetCalenderList?fromDate="
            "{}&toDate={}&meetingType=1&committeeId=null&pageCount=1000&offsetStart=0"
            "&abbreviation=undefined&keywords="
        ).format(start_date.strftime(date_input_format), end_date.strftime(date_input_format))
        
        req = self.get(events_url)
        rows = json.loads(req.content)
        for row in rows:
            yield from self.scrape_event(row)

    def scrape_event(self, row):
        location = row["Address"]

        if not location:
            location = "Not Provided"

        # 2020-04-29T13:30:00
        event_date_str = row["MeetingTime"]
        event_date = dt.datetime.strptime(event_date_str, "%Y-%m-%dT%H:%M:%S")
        event_date = self.TIMEZONE.localize(event_date)

        description = str(row["Description"])

        status = ""
        if event_date > self.TIMEZONE.localize(dt.datetime.today()):
            status = "tentative"
        else:
            status = "passed"

        if "cancellation" in description.lower() or "cancelled" in description.lower():
            status = "cancelled"

        event = Event(
            name=row["CommitteeName"],
            start_date=event_date,
            location_name=location,
            status=status,
            description=description,
        )

        if row["CommitteeName"]:
            event.add_participant(name=row["CommitteeName"], type="organization")

        if row["MarkedAgendaPublished"]:
            agenda_url = self.AGENDA_URL.format(
                com_abbr=row["Abbreviation"], id=row["AgendaId"]
            )
            event.add_document("Agenda", agenda_url, media_type="text/html")

            agenda_req = self.get(agenda_url).content
            agenda_page = lxml.html.fromstring(agenda_req)
            agenda_page.make_links_absolute("https://lims.minneapolismn.gov/")

            agenda_item = event.add_agenda_item("Bills")
            for bill_link in agenda_page.xpath('//a[contains(@href, "/File/")]'):
                bill_id = bill_link.xpath("text()")[0].strip()
                bill_id = bill_id.replace("(", "").replace(")", "")
                agenda_item.add_bill(bill_id)
        event.add_source("https://lims.minneapolismn.gov/Calendar/all/monthly")
        yield event
