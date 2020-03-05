import datetime
import re

import pytz
import requests
from legistar.events import LegistarAPIEventScraperZip
from utils.novusagenda import NovusAgendaScraper
from pupa.scrape import Event, Scraper

class BakersfieldEventScraper(NovusAgendaScraper, Scraper):
    BASE_URL = "https://bakersfield.novusagenda.com/AgendaPublic/"
    TIMEZONE = pytz.timezone("America/Los_Angeles")
