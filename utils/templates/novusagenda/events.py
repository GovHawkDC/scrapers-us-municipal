import datetime
import re

import pytz
import requests
from utils.novusagenda import NovusAgendaScraper
from pupa.scrape import Event, Scraper

class {{ class_name }}EventScraper(NovusAgendaScraper, Scraper):
    BASE_URL = "{{ url }}"
    TIMEZONE = pytz.timezone("{{ timezone }}")
