import datetime
import re

import pytz
import requests
from utils.sire import SireScraper
from pupa.scrape import Event, Scraper

class {{ class_name }}EventScraper(SireScraper, Scraper):
    BASE_URL = "{{ url }}"
    TIMEZONE = pytz.timezone("{{ timezone }}")
