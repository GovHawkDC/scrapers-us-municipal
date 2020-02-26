from pupa.scrape import Bill, VoteEvent, Scraper
from pupa.utils import _make_pseudo_id
import datetime
import itertools
import pytz
import requests
import re
import lxml.html

class HoustonBillScraper(Scraper):
    BASE_URL = "https://houston.novusagenda.com/agendapublic/"
    TIMEZONE = pytz.timezone("America/Chicago")

    ORDINANCE_NO_REGEX = r'^(HPW)*[\s|–\-]*(\w+[\-\d+B]*)'

    s = requests.Session()

    def session(self, action_date):
        return str(action_date.year)

    def scrape(self, window=3):
        n_days_ago = datetime.datetime.utcnow() - datetime.timedelta(float(window))

        params = {
            'ctl00$ContentPlaceHolder1$radScriptManagerMain': 'ctl00$ContentPlaceHolder1$radScriptManagerMain|ctl00$ContentPlaceHolder1$SearchAgendasMeetings$imageButtonSearch',
            'ctl00_ContentPlaceHolder1_radScriptManagerMain_TSM': ';;System.Web.Extensions, Version=4.0.0.0, Culture=neutral, PublicKeyToken=31bf3856ad364e35:en-US:9ead301a-2c07-4fc5-be19-f8423a34e117:ea597d4b:b25378d2;Telerik.Web.UI, Version=2016.1.225.45, Culture=neutral, PublicKeyToken=121fae78165ba3d4:en-US:66ff0eae-58a2-4708-afa3-f38f5cdcfcc6:16e4e7cd:ed16cbdc:f7645509:88144a7a:7c926187:8674cba1:b7778d6c:c08e9f8a:4877f69a:24ee1bba:92fe8ea0:fa31b949:874f8ea2:c128760b:19620875:f46195d3:490a9d4e:bd8f85e4:e330518b:1e771326:8e6f0d33:1f3a7489:6a6d718d:58366029:2003d0b8:aa288e2d:258f1c72:59462f1:a51ee93e;',
            'ctl00$ContentPlaceHolder1$SearchAgendasMeetings$ddlDateRange': 'cus',
            'ctl00$ContentPlaceHolder1$SearchAgendasMeetings$radCalendarFrom': '2019-01-01',
            'ctl00$ContentPlaceHolder1$SearchAgendasMeetings$radCalendarFrom$dateInput': '1/1/2019',
            'ctl00_ContentPlaceHolder1_SearchAgendasMeetings_radCalendarFrom_dateInput_ClientState': '{"enabled":true,"emptyMessage":"","validationText":"2019-01-01-00-00-00","valueAsString":"2019-01-01-00-00-00","minDateStr":"1970-01-01-00-00-00","maxDateStr":"2099-12-31-00-00-00","lastSetTextBoxValue":"1/1/2019"}',
            'ctl00_ContentPlaceHolder1_SearchAgendasMeetings_radCalendarFrom_ClientState': '{"minDateStr":"1970-01-01-00-00-00","maxDateStr":"2099-12-31-00-00-00"}',
            'ctl00$ContentPlaceHolder1$SearchAgendasMeetings$radCalendarTo': '2020-05-25',
            'ctl00$ContentPlaceHolder1$SearchAgendasMeetings$radCalendarTo$dateInput': '5/25/2020',
            'ctl00_ContentPlaceHolder1_SearchAgendasMeetings_radCalendarTo_dateInput_ClientState': '{"enabled":false,"emptyMessage":"","validationText":"2020-05-25-00-00-00","valueAsString":"2020-05-25-00-00-00","minDateStr":"1970-01-01-00-00-00","maxDateStr":"2099-12-31-00-00-00","lastSetTextBoxValue":"5/25/2020"}',
            'ctl00_ContentPlaceHolder1_SearchAgendasMeetings_radCalendarTo_ClientState': '{"minDateStr":"1970-01-01-00-00-00","maxDateStr":"2099-12-31-00-00-00"}',
            'ctl00$ContentPlaceHolder1$SearchAgendasMeetings$ctl00': '-1',
            'ctl00$ContentPlaceHolder1$SearchAgendasMeetings$ctl01': '-1',
            'ctl00$ContentPlaceHolder1$SearchAgendasMeetings$ctl02': '',
            'ctl00_ContentPlaceHolder1_SearchAgendasMeetings_radWindowPublicVOD_ClientState': '',
            'ctl00_ContentPlaceHolder1_SearchAgendasMeetings_radWindowPublicStream_ClientState': '',
            'ctl00_ContentPlaceHolder1_SearchAgendasMeetings_ctl04_ClientState': '',
            'ctl00_ContentPlaceHolder1_SearchAgendasMeetings_radTSMain_ClientState': '{"selectedIndexes":["0"],"logEntries":[],"scrollState":{}}',
            'ctl00$ContentPlaceHolder1$SearchAgendasMeetings$radGridMeetings$ctl00$ctl03$ctl01$PageSizeComboBox': '15',
            'ctl00_ContentPlaceHolder1_SearchAgendasMeetings_radGridMeetings_ctl00_ctl03_ctl01_PageSizeComboBox_ClientState': '',
            'ctl00_ContentPlaceHolder1_SearchAgendasMeetings_radGridMeetings_ClientState': '',
            'ctl00$ContentPlaceHolder1$SearchAgendasMeetings$radGridItems$ctl00$ctl03$ctl01$PageSizeComboBox': '15',
            'ctl00_ContentPlaceHolder1_SearchAgendasMeetings_radGridItems_ctl00_ctl03_ctl01_PageSizeComboBox_ClientState': '',
            'ctl00_ContentPlaceHolder1_SearchAgendasMeetings_radGridItems_ClientState': '',
            'ctl00_ContentPlaceHolder1_SearchAgendasMeetings_radMPMain_ClientState': '',
            'ctl00_ContentPlaceHolder1_SearchAgendasMeetings_sharedDynamicCalendar_SD': '[]',
            'ctl00_ContentPlaceHolder1_SearchAgendasMeetings_sharedDynamicCalendar_AD': '[[1970,1,1],[2099,12,30],[2020,2,25]]',
            'RadAJAXControlID': 'ctl00_ContentPlaceHolder1_radAjaxManagerMain',        
        }

        html = self.asp_post(self.BASE_URL, params)
        page = lxml.html.fromstring(html)

        bill_column_map = {}
        row_index = 1
        for row in page.xpath('//table[@id="ctl00_ContentPlaceHolder1_SearchAgendasMeetings_radGridItems_ctl00"]/thead/tr[1]/th'):
            row_text = row.text_content().strip()
            if row_text != '' and row_text != '&nbsp;':
                bill_column_map[row_text] = row_index
            row_index += 1

        print(bill_column_map)

        for row in page.xpath('//table[@id="ctl00_ContentPlaceHolder1_SearchAgendasMeetings_radGridItems_ctl00"]/tbody/tr[contains(@class,"rgRow") or contains(@class,"rgAltRow")]'):
            yield from self.parse_bill_row(bill_column_map, row)

    def parse_bill_row(self, bill_column_map, row):
        item_type = row.xpath('td[{}]/text()'.format(bill_column_map['Category']))[0].strip()
        if item_type != 'ORDINANCES':
            return

        date_text = row.xpath('td[{}]/text()'.format(bill_column_map['Date']))[0].strip()
        bill_date = self.TIMEZONE.localize(
            datetime.datetime.strptime(date_text, "%m/%d/%y")
        )

        item_title = row.xpath('td[{}]/text()'.format(bill_column_map['Title']))[0].strip()
        if re.search(self.ORDINANCE_NO_REGEX, item_title):
            match = re.search(self.ORDINANCE_NO_REGEX, item_title)
            bill_no = match.group(2)
            bill_title = item_title
        else:
            self.info("NO regex match for {}, passing", item_title)
            return

        bill = Bill(
            bill_no,
            str(bill_date.year),
            bill_title,
            from_organization={"name": "Houston City Council"}
        )
        bill.add_source(self.BASE_URL)
        yield bill
        # print(bill_no)
        # print(bill_title)

        # date_text = row.xpath('td[{}]/text()'.format(event_column_map['Meeting Date']))[0].strip()
        # event_date = datetime.datetime.strptime(date_text, "%m/%d/%y")

        # event_type = row.xpath('td[{}]/text()'.format(event_column_map['Meeting Type']))[0].strip()

        # event_location = row.xpath('td[{}]/text()'.format(event_column_map['Meeting Location']))[0].strip()

        # event = Event(name=event_type,
        #             start_date=event_date,
        #             # description=description,
        #             location_name=event_location,
        #             )

        # event.add_source(self.BASE_URL)

        # yield event


    def asp_post(self, url, params, page=None):
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/79.0.3945.117 Safari/537.36",
            "referer": url,
            # "origin": url,
            # "authority": url,
        }

        if page is None:
            page = self.s.get(url, headers=headers)
            page = lxml.html.fromstring(page.content)

        (viewstate,) = page.xpath('//input[@id="__VIEWSTATE"]/@value')
        (viewstategenerator,) = page.xpath('//input[@id="__VIEWSTATEGENERATOR"]/@value')

        form = {
            "__VIEWSTATE": viewstate,
            "__VIEWSTATEGENERATOR": viewstategenerator,
            # "__EVENTVALIDATION": eventvalidation,
            "__LASTFOCUS": "",
            "__ASYNCPOST": "",
        }

        form = {**form, **params}

        response_text = self.s.post(url, data=form, headers=headers).text
        return response_text        