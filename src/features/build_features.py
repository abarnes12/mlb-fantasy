# need to provide a list of years to consider
# need to separate out batting and pitching
# need to make draft metric based on past 3 years for each player
# want to group results by position
# fill positions in draft with top choices
# once core positions are filled, focus on selecting top players regardless of position? try to spread it out I guess
# maybe want a balance between all of the categories since I can only get a maximum number of points in a single category

# maybe the single spot positions bid later since the 13+ person could still be good
# in this case, outfield and pitchers first?

# this is complicated. start simple. not sure how to get easy list of eligibility
from pathlib import Path
import argparse

import pandas as pd

import features


def build_features():
    """Process raw data into usable tables"""

    # parse arguments
    parser = argparse.ArgumentParser(description="Process raw data into usable tables")
    parser.add_argument('--league', default='mlb')
    parser.add_argument('--season', default='2018-regular')
    parser.add_argument('--feed', default='cumulative_player_stats')
    parser.add_argument('--format', default='csv')
    parser.add_argument('--msf', action='store_true', default=False)
    args = parser.parse_args()

    base_dir = Path.cwd()
    base_dir = base_dir / '..' / '..'
    base_dir = base_dir.resolve()
    raw_dir = base_dir / 'data' / 'raw'
    processed_dir = base_dir / 'data' / 'processed'

    if args.msf:
        filename = args.feed + '-' +  args.league + '-' + args.season + '.' + args.format

        text = []
        with open(raw_dir / filename, 'r') as csvfile:
            for line in csvfile:
                text.append(line.split("', '"))
        
        labels = []
        for i in range(len(text[0])):
            text[0][i] = text[0][i].strip('#')
            labels.append(text[0][i])
        
        for i in range(len(text)):
            text[i][-1] = text[i][-1].split("']")[0]
        
        df_text = pd.DataFrame(text[1:], columns=text[0])
        df_text.drop([labels[0]], axis=1, inplace=True)

        to_drop = ['Jersey Num', 'Height', 'Weight', 'Birth Date', 'Age', 'Birth City', 'Birth Country', 'Rookie',
                   'Team ID', 'Team Abbr.', 'Team City', 'Team Name', 'RunsAllowed']
        df_text.to_csv(processed_dir / filename, index=False)
    else:
        # call a feature building class and make use of it here
        draft_builder = features.DraftBuilder()
        years = ['2016', '2017', '2018']
        draft_builder.make_draft(years, True)
        draft_builder.make_draft(years, False)

    return

if __name__ == "__main__":
    build_features()
