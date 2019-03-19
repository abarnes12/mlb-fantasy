import configparser
from pathlib import Path
import re

from ohmysportsfeedspy import MySportsFeeds
import urllib3
import certifi
from bs4 import BeautifulSoup as BS
from bs4 import Comment
import pandas as pd


class Scraper(object):
    """Scraper class for gathering statistics from MySportsFeeds"""

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

    def get_data(self, league='mlb', season='2018-regular', feed='cumulative_player_stats',
                 format='csv', playerstats='all'):
        """Get data from MySportsFeeds and automatically write results to `store_location`"""
        if len(playerstats) == 'all':
            output = self.msf.msf_get_data(league=league,
                                           season=season,
                                           feed=feed,
                                           format=format,
                                          )
        else:
            print(playerstats)
            output = self.msf.msf_get_data(league=league,
                                           season=season,
                                           feed=feed,
                                           format=format,
                                           playerstats=playerstats,
                                           force='true'
                                          )
        return


class Scraper_BS(object):
    """Scraper class using BeautifulSoup to parse baseball-reference.com tables"""

    # Constructor
    def __init__(self):
        self.http = urllib3.PoolManager(cert_reqs='CERT_REQUIRED', ca_certs=certifi.where())

    def get_data(self, url, stats_to_keep):
        tablename = url.split('#')[-1].split(':')[0]
        filename = url.split('#')[0].split('/')[-1].split('.')[0]

        response = self.http.request('GET', url)
        # initial soup but desired table is buried in a comment
        soup = BS(response.data, features='lxml')
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))

        # find table using tablename string
        idx = 0
        for i in range(len(comments)):
            if tablename in comments[i]:
                idx = i

        # update soup to contain desired table
        new_html = comments[idx]
        soup = BS(new_html, features='html.parser')
        table = soup.find(lambda tag: tag.name=='table' and tag.has_attr('id') and tag['id']==tablename)
        rows = table.findAll(lambda tag: tag.name=='tr')

        players = {}
        for i in range(len(rows)):
            stats = {}
            player = ''
            for child in rows[i].children:
                try:
                    #if child.attrs['data-stat'] in 'pos_summary':
                    #    stat = child.attrs['data-stat']
                    #    value = child.contents[0]
                    #    stats[stat] = value
                    if child.attrs['data-stat'] in stats_to_keep:
                        stat = child.attrs['data-stat']
                        if len(child.contents) > 0:
                            value = child.contents[0]
                        else:
                            value = None
                        stats[stat] = value
                    if child.attrs['data-stat'] in 'player':
                        player = child.contents[0].string
                except AttributeError:
                    break
            not_real = False
            for stat in stats_to_keep:
                if stat not in list(stats.keys()):
                    stats[stat] = None
                if stats[stat] is not None and stat not in 'pos_summary':
                    try:
                        stats[stat] = float(stats[stat])
                    except ValueError:
                        not_real = True
            if not_real:
                break
            #if 'pos_summary' in list(stats.keys()):
            #    stats_to_keep.append('pos_summary')
            players[player] = [stats[stat] for stat in stats_to_keep]

        df = pd.DataFrame.from_dict(players, orient='index', columns=stats_to_keep)
        base_dir = Path.cwd()
        base_dir = base_dir / '..' / '..'
        data_dir = base_dir / 'data' / 'raw'
        data_dir.resolve()
        filename = str(data_dir) + '/' + filename + '.csv'
        df['player'] = df.index
        df.drop(df.index[0], inplace=True)
        df.to_csv(filename, index=False)

        return
