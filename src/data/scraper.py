import configparser
from pathlib import Path

from ohmysportsfeedspy import MySportsFeeds


class Scraper(object):
    """Scraper class for gathering statistics from online resources"""

    # Constructor
    def __init__(self, base_dir=None):
        (api_key, api_passwd, api_version) = self._get_config(base_dir)
        self.api_version = api_version
        self.msf = self._get_msf(base_dir, api_version)
        self.msf.authenticate(api_key, api_passwd)

    def _get_config(self, base_dir):
        """Read in configuration information for the MySportsFeeds API"""

        config = configparser.ConfigParser()
        config.read(base_dir / 'config.ini')
        api_key = config['DEFAULT']['API_KEY']
        api_passwd = config['DEFAULT']['PASSWORD']
        api_version = config['DEFAULT']['VERSION']

        return (api_key, api_passwd, api_version)

    def _get_msf(self, base_dir, api_version):
        store_location = base_dir / 'data' / 'raw'
        store_location = str(store_location) + '/'
        msf = MySportsFeeds(version=api_version, store_location=store_location)

        return msf

    def get_data(self, league='mlb', season='2018-regular', feed='cumulative_player_stats', format='csv'):
        """Get data from MySportsFeeds and automatically write results to `store_location`"""
        output = self.msf.msf_get_data(league=league,
                                       season=season,
                                       feed=feed,
                                       format=format,
                                      )
        return
