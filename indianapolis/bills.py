import datetime
import json
import pytz
from pupa.scrape import Scraper
from pupa.scrape import Bill


class IndianapolisBillScraper(Scraper):
    TIMEZONE = pytz.timezone('America/Indiana/Indianapolis')

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
                chamber='upper',
                title=row['digest'],
                classification=self.classify(row['proposal_type']),
            )

            for sponsor in row['sponsors'].splitlines():
                sponsor = sponsor.replace('President','')
                sponsor = sponsor.replace('Councilor', '')
                sponsor = sponsor.strip()
                
                bill.add_sponsorship(
                    name=sponsor,
                    classification="primary",
                    entity_type="person",
                    primary=True
                )

            for version in row['document_list']:
                version_url = 'https://www.indy.gov{}'.format(version['content_link'])

                bill.add_version_link(
                    version['name'],
                    version_url,
                    media_type=version['content_type'],
                    on_duplicate='ignore'
                )

            for action in row['action_list']:
                action_date = self.TIMEZONE.localize(
                    datetime.datetime.strptime(
                        action['action_date'],
                        '%Y-%m-%d'
                    )
                )

                classification = None
                if 'adopted' in action['action_description'].lower():
                    classification = 'passage'

                bill.add_action(
                    action['action_description'],
                    action_date,
                    classification=classification
                )

                if row['ordinance_number'] != 0:
                    bill.extras['ordinance_number'] = row['ordinance_number']

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
