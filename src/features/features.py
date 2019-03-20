from pathlib import Path

import pandas as pd
import numpy as np


class DraftBuilder(object):
    """Class used to build features from baseball-reference input for drafting"""

    # useful variables

    # Constructor
    def __init__(self):
        self.positions = ['C', '1B', '2B', '3B', 'SS', 'OF', 'Util', 'SP', 'RP', 'P', 'BN', 'DL']

    # need to determine fielding positions for batters and pitchers
    # calculate total games started and games finished for pitchers
    # extract field positions from pos_summary and turn it into a column
    # concatenate multiple years in order to determine eligibility
    # concatenate batting and pitching to make one large table

    def _make_cols(self, df):
        """Make columns for each spot allowed in the roster"""
        n_players = df.shape[0]
        zeros = [0 for n in range(n_players)]
        for pos in self.positions:
            df[pos] = zeros
        return df

    def _concat(self, dfs):
        """Concatenate multiple dataframes"""
        return pd.concat(dfs, ignore_index=True)

    def _parse_position(self, df):
        """Parse the position for batters"""
        df['pos_summary'] = df['pos_summary'].apply(lambda x: str(x).strip('D*').split('/')[0])
        df = self._make_cols(df)
        pos_dict = {
                    1: 'P',
                    2: 'C',
                    3: '1B',
                    4: '2B',
                    5: '3B',
                    6: 'SS',
                    7: 'OF',
                    8: 'OF',
                    9: 'OF',
                   }

        def split_pos(s):
            pos_list = list(s['pos_summary'])
            if len(pos_list) == 0:
                return
            for pos in pos_list:
                if not pos.isdigit():
                    continue
                col = pos_dict[int(pos)]
                s[col] = 1
            return s

        return df.apply(lambda x: split_pos(x), axis=1)

    def _summarize(self, df, is_pitcher):
        """Summarize statistics from multiple years"""
        if is_pitcher:
            df['W/IP'] = df['W'].div(df['IP'])
            df['SV/IP'] = df['SV'].div(df['IP'])
            df['SO/IP'] = df['SO'].div(df['IP'])
            agg_dict = {
                        'W/IP': 'mean',
                        'SV/IP': 'mean',
                        'SO/IP': 'mean',
                        'earned_run_avg': 'mean',
                        'whip': 'mean',
                        'GS': 'sum',
                        'GF': 'sum',
                       }
            return df.groupby('player').agg(agg_dict).reset_index()
        else:
            df = self._parse_position(df)
            df['R/G'] = df['R'].div(df['G'])
            df['HR/G'] = df['HR'].div(df['G'])
            df['RBI/G'] = df['RBI'].div(df['G'])
            df['SB/G'] = df['SB'].div(df['G'])
            agg_dict = {
                        'R/G': 'mean',
                        'HR/G': 'mean',
                        'RBI/G': 'mean',
                        'SB/G': 'mean',
                        'batting_avg': 'mean',
                        'P': 'sum',
                        'C': 'sum',
                        '1B': 'sum',
                        '2B': 'sum',
                        '3B': 'sum',
                        'SS': 'sum',
                        'OF': 'sum',
                       }
            df_new = df.groupby('player').agg(agg_dict).reset_index()
            for pos in ['P', 'C', '1B','2B', '3B', 'SS', 'OF']:
                df_new[pos] = df_new[pos].apply(lambda x: np.where(x>0, 1, 0))
            return df_new

    def make_draft(self, years, is_pitcher):
        """Make a draft dataframe based on `years`"""
        if is_pitcher:
            base_file = '-standard-pitching.csv'
        else:
            base_file = '-standard-batting.csv'
        base_dir = Path.cwd()
        base_dir = base_dir / '..' / '..'
        raw_dir = base_dir / 'data' / 'raw'
        raw_dir = raw_dir.resolve()

        filename = str(raw_dir) + '/' + years[0] + base_file
        df = pd.read_csv(filename)
        for y in range(1,len(years)):
            filename = str(raw_dir) + '/' + years[y] + base_file
            df_tmp = pd.read_csv(filename)
            df = self._concat([df, df_tmp])

        df = self._summarize(df, is_pitcher)

        processed_dir = base_dir / 'data' / 'processed'
        processed_dir = processed_dir.resolve()
        filename = str(processed_dir) + '/draft' + base_file
        df.to_csv(filename, index=False)
