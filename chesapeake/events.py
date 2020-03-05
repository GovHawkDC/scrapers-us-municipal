import pytz
from pupa.scrape import Scraper
from pupa.scrape import Event
from utils.granicus import GranicusScraper


class ChesapeakeEventScraper(GranicusScraper, Scraper):

    BASE_URL = "http://chesapeake.granicus.com/ViewPublisher.php?view_id=2"
    TIMEZONE = pytz.timezone("America/New_York")