import datetime
import json
from pupa.scrape import Scraper
from pupa.scrape import Bill


class IndianapolisBillScraper(Scraper):

    def scrape(self):
        year = datetime.datetime.today().year

        url = 'https://www.indy.gov/api/v1/indy_find_proposals?__workflow_id=&year={}' \
            '&proposal_number=&ordinance_number=&proposal_type=&councillor=&committee=&initiator=&keywords='

        url = url.format(year)
        page = self.get(url).content
        page = json.loads(page)

        for row in page['data']:

            identifier = 'PROP{}-{}'.format(
                str(year)[2:],
                "{:03d}".format(row['proposal_number'])
            )
            

            bill = Bill(
                identifier=identifier,
                legislative_session=str(year),
                title=row['digest'],
                classification=self.classify(row['proposal_type']),
            )
            bill.add_source('https://www.indy.gov/workflow/city-county-council-proposals')

            yield bill

    def classify(self, classification):
        classes = {
            'General Resolution': 'resolution',
            'Council Resolution': 'resolution',
            'Rezoning Ordinance': 'ordinance',
            'Fiscal Ordinance':'ordinance',
            'General Ordinanace':'ordinance',
            'Special Ordinance':'ordinance',
        }

        if classification in classes:
            return classes[classification]
        else:
            return 'bill'
