import argparse
from pathlib import Path

import scraper


def make_dataset():
    """Pull statistics from an online resource and save to the data/raw directory"""

    # parse arguments
    parser = argparse.ArgumentParser(description="Gather player statistics from an online resource")
    parser.add_argument('--league', default='mlb')
    parser.add_argument('--season', default='2018-regular')
    parser.add_argument('--feed', default='cumulative_player_stats')
    parser.add_argument('--format', default='csv')
    parser.add_argument('--msf', action='store_true', default=False)
    args = parser.parse_args()

    # get scraper
    base_dir = Path.cwd()
    base_dir = base_dir / '..' / '..'
    base_dir = base_dir.resolve()
    if args.msf:
        scraper_ = scraper.Scraper(base_dir=base_dir)
        playerstats = ['R', 'HR', 'RBI', 'SB', 'AVG', 'W', 'SV', 'IP', 'SO', 'WHIP', 'ERA']
        scraper_.get_data(league=args.league, season=args.season, feed=args.feed,
                          format=args.format, playerstats=playerstats)
    else:
        scraper_ = scraper.Scraper_BS()
        base_url = 'https://www.baseball-reference.com/leagues/' + args.league + '/'

        # batting
        stats_to_keep = ['G', 'R', 'HR', 'RBI', 'SB', 'batting_avg']
        # season: YYYY
        url = base_url + args.season + '-standard-batting.shtml#players_standard_batting::none'
        scraper_.get_data(url, stats_to_keep)

        # pitching
        stats_to_keep = ['W', 'SV', 'SO', 'ERA', 'WHIP', 'IP']
        url = base_url + args.season + '-standard-pitching.shtml#players_standard_pitching::none'
        scraper_.get_data(url, stats_to_keep)

    return


if __name__ == "__main__":
    make_dataset()
