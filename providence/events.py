import pytz
from pupa.scrape import Scraper
from pupa.scrape import Event
from utils.iq2m import IQ2MScraper

class ProvidenceEventScraper(IQ2MScraper, Scraper):
    BASE_URL = "http://providenceri.iqm2.com/"
    TIMEZONE = pytz.timezone("America/New_York")
    JURIS_NAME = "Providence"