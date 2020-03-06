import pytz
from pupa.scrape import Scraper
from pupa.scrape import Event
from utils.iq2m import IQ2MScraper

class {{ class_name }}EventScraper(IQ2MScraper, Scraper):
    BASE_URL = "{{ url }}"
    TIMEZONE = pytz.timezone("{{ timezone }}")
    JURIS_NAME = "{{ city_name }}"