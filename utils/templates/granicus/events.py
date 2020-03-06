import pytz
from pupa.scrape import Scraper
from pupa.scrape import Event
from utils.granicus import GranicusScraper


class {{ class_name }}EventScraper(GranicusScraper, Scraper):
    BASE_URL = "{{ url }}"
    TIMEZONE = pytz.timezone("{{ timezone }}")
