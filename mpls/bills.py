from pupa.scrape import Scraper
from pupa.scrape import Bill


class MplsBillScraper(Scraper):

    def scrape(self):
        # needs to be implemented
        
        # https://lims.minneapolismn.gov/Search?a&q=&count=3&fdate=01%2F01%2F2020&s=fmd&tdate=03%2F31%2F2020
        # there's a POST to csv export there
        # and then in the bill pages
        # var model = JSON OBJECT with what we want?
        pass
