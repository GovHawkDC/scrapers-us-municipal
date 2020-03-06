import datetime
import re

import pytz
import requests
from utils.agendacenter import AgendaCenterScraper
from pupa.scrape import Event, Scraper

class {{ class_name }}EventScraper(AgendaCenterScraper, Scraper):
    BASE_URL = "{{ url }}"
    TIMEZONE = pytz.timezone("{{ timezone }}")
