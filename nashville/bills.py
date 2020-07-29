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

        header = page.xpath('//div[contains(@id,"LegislationDetails")]/h1/text()')[0]
        bill_number = re.search(r"\w{2}\d{4}-\d+", header).group(0)

        print(bill_number)

        yield {}

    # extract the session from the listing page header
    def scrape_session(self, page):
        header = page.xpath('string(//h1[contains(text(), "Resolution")])')
        print(header)
        return re.search(r"\d{4}-\d{4}", header).group(0)
