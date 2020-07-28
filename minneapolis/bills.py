from pupa.scrape import Scraper
from pupa.scrape import Bill

import requests
import csv
import datetime as dt
import pprint

class MinneapolisBillScraper(Scraper):
    def scrape(self, start_date=None, end_date=None):
        if start_date is None:
            start_date = dt.datetime.today() + dt.timedelta(days=30)
        else:
            start_date = dt.datetime.strptime(end_date, "%Y-%m-%d")

        if end_date is None:
            end_date = dt.datetime.today() + dt.timedelta(days=30)
        else:
            end_date = dt.datetime.strptime(end_date, "%Y-%m-%d")


        # url = "https://lims.minneapolismn.gov/home/LegislationsSearchResultExportCSV"

        url = 'https://lims.minneapolismn.gov/home/SearchLegislations'

        headers = {
            'authority': 'lims.minneapolismn.gov',
            'accept': 'application/json, text/plain, */*',
            'dnt': '1',
            'data-type': 'json',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.92 Safari/537.36',
            'content-type': 'application/json; charset=UTF-8',
            'origin': 'https://lims.minneapolismn.gov',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://lims.minneapolismn.gov/Search?q=&page=1&cid=1&scid=1&wid=1&s=fmd&a&tid=&fdate=04%2F01%2F2020',
            'accept-language': 'en-US,en;q=0.9',
            # 'cookie': '__cfduid=d6198ed8c542e851a7473f09624eb84401588107681; lims-dmz-https-443_443-%3Fmpl-dmz%3Flims-dmz-https-443=BHAPBLKM',
        }

        data = '{"totalItems":15105,"FileNumberAscending":null,"FileModifiedAscending":false,"PageSize":100,"PageNumber":1,"Keyword":"","RCACategoryId":1,"RCASubCategoryId":1,"IntroducedFromDate":null,"IntroducedToDate":null,"ToDate":null,"FromDate":"04/01/2020","Department":null,"Committee":null,"ReferredToCommittee":null,"Author":null,"WardId":1,"NeighborHoodName":"Select Neighborhood","AdvancedSearch":true,"LegislativeStatusId":"","CommitteeId":null,"DepartmentId":null,"ReferredToCommitteeId":null,"AuthorId":null,"NoMaster":true,"TermId":""}'

        bills = self.post(url, data=data, headers=headers).json()
        for row in bills['Entity']:
            yield from self.scrape_bill(row)

    def scrape_bill(self, row):
        pprint.pprint(row)

        bill = Bill(
            identifier=row['FileNumber'],
            session=row['FileNumber'][0:4],
            title=row['FileSubject']
        )

        yield {}
