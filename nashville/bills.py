import lxml.html
import re
from pupa.scrape import Scraper
from pupa.scrape import Bill


class NashvilleBillScraper(Scraper):
    session = None

    def scrape(self, session=None):
        if session is None:
            session_url = 'https://www.nashville.gov/Metro-Clerk/Legislative/Resolutions.aspx'
            page = self.get(session_url).content
            page = lxml.html.fromstring(page)
            page.make_links_absolute(session_url)

            res_link = page.xpath('//div[@id="dnn_ctr3317_HtmlModule_lblContent"]/p/a[contains(@href,"/Legislative/Resolutions/")]/@href')[0]
            ord_link = res_link.replace('/Resolutions/', '/Ordinances/')

            yield from self.scrape_index(res_link)
            yield from self.scrape_index(ord_link)

    def scrape_index(self, url):
        print(url)
        page = self.get(url).content
        page = lxml.html.fromstring(page)
        page.make_links_absolute(url)

        if not self.session:
            self.session = self.scrape_session(page)

        for row in page.xpath('//a[contains(@id,"LegislationList")]/@href'):
            yield from self.scrape_bill(row)

    def scrape_bill(self, url):
        page = self.get(url).content
        page = lxml.html.fromstring(page)
        page.make_links_absolute(url)

        bill_title = page.xpath('//div[contains(@id,"LegislationDetails")]/h1/text()')[0]
        identifier = re.search(r"\w{2}\d{4}-\d+", bill_title).group(0)

        if '/Ordinances/' in url:
            bill_type = 'ordinance'
        else:
            bill_type = 'resolution'

        bill = Bill(
            identifier=identifier,
            legislative_session=self.session,
            chamber='upper',
            title=bill_title,
            classification=bill_type,
        )
        # TODO: Versions, Actions, Sponsors

        sponsors_text = page.xpath('//h2[contains(text(), "Sponsor(s)")]//following-sibling::p[1]/text()')[0]
        sponsors = sponsors_text.split(",")

        for sponsor in sponsors:
            bill.add_sponsorship(
                sponsor.strip(),
                classification="primary",
                entity_type="person",
                primary=True
            )

        for doc_link in page.xpath('//h2[contains(text(), "Documents")]//following-sibling::ul[1]/li/a'):
            doc_url = doc_link.xpath('@href')[0]
            doc_name = doc_link.xpath('text()')[0].replace('Download ','').strip()
            bill.add_version_link(
                doc_name,
                doc_url
            )

        bill.add_source(url)

        yield bill

    # extract the session from the listing page header
    def scrape_session(self, page):
        header = page.xpath('string(//h1[contains(text(), "Resolution")])')
        print(header)
        return re.search(r"\d{4}-\d{4}", header).group(0)
