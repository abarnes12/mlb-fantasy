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
    args = parser.parse_args()

    # get scraper
    base_dir = Path.cwd()
    base_dir = base_dir / '..' / '..'
    base_dir = base_dir.resolve()
    scraper_ = scraper.Scraper(base_dir=base_dir)
    scraper_.get_data(league=args.league, season=args.season, feed=args.feed, format=args.format)

    return


if __name__ == "__main__":
    make_dataset()
