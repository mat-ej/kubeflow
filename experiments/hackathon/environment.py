import numpy as np
import pandas as pd


class Environment:
    def __init__(self, dataset, interactor, init_bankroll=1000, min_bet=5, max_bet=100):
        dataset['BetH'] = 0.
        dataset['BetD'] = 0.
        dataset['BetA'] = 0.
        self.dataset = dataset
        self.interactor = interactor
        self.bankroll = init_bankroll
        self.min_bet = min_bet
        self.max_bet = max_bet
        self.last_seen = pd.to_datetime('1900-01-01')
        self.bet_cols = ['BetH', 'BetD', 'BetA']
        self.odds_cols = ['OddsH', 'OddsD', 'OddsA']
        self.score_cols = ['HSC', 'ASC']
        self.res_cols = ['H', 'D', 'A']
        self.label_cols = self.score_cols + self.res_cols

    def get_incremental_data(self, date):
        inc = self.dataset.loc[(self.dataset.Date > self.last_seen) & (self.dataset.Date < date)]
        self.last_seen = inc.Date.max() if not inc.empty else self.last_seen
        return inc

    def get_opps(self, date):
        opps = self.dataset[(self.dataset.Open <= date) & (self.dataset.Date >= date)]
        opps = opps[opps[self.odds_cols].sum(axis=1) > 0]
        return opps.drop(self.label_cols, axis=1)

    def run(self, start=None, end=None):
        start = start if start is not None else self.dataset.Open.min()
        end = end if end is not None else self.dataset.Date.max()

        print(f"Start: {start}, End: {end}")
        for date in pd.date_range(start, end):

            opps = self.get_opps(date)
            if opps.empty:
                continue

            inc = self.get_incremental_data(date)
            
            placed = opps[self.bet_cols].sum().sum()

            self.bankroll += self.evaluate_bets(inc)

            summary = self.generate_summary(date)
            print(f'{date:%Y-%m-%d}: available: {self.bankroll:.2f}, invested {placed:.2f}, total {self.bankroll+placed:.2f}')

            bets = self.get_bets(summary, inc, opps)

            validated_bets = self.validate_bets(bets, opps)

            self.place_bets(validated_bets)

        self.bankroll += self.evaluate_bets(self.get_incremental_data(end + pd.to_timedelta(1, 'days')))

        if hasattr(self.interactor, 'writeln'):
            self.send_updates(pd.DataFrame(), pd.DataFrame(), pd.DataFrame())

        return self.dataset

    def validate_bets(self, bets, opps):
        #print("Validating bets")
        rows = bets.index.intersection(opps.index)
        cols = bets.columns.intersection(self.bet_cols)
        validated_bets = bets.loc[rows, cols]  # allow bets only on the send opportunities
        validated_bets[validated_bets < self.min_bet] = 0.  # reject bets lower than min_bet
        validated_bets[validated_bets > self.max_bet] = 0.  # reject bets higher than max_bet
        if validated_bets.sum().sum() > self.bankroll:  # reject bets if there are no sufficient funds left
            validated_bets.loc[:, :] = 0.
        return validated_bets

    def place_bets(self, bets):
        #print("Placing bets")
        self.dataset.loc[bets.index, self.bet_cols] = self.dataset.loc[bets.index, self.bet_cols].add(bets, fill_value=0)
        self.bankroll -= bets.values.sum()

    def evaluate_bets(self, inc):
        if inc.empty:
            return 0
        b = inc[self.bet_cols].values
        o = inc[self.odds_cols].values
        r = inc[self.res_cols].values
        winnings = (b * r * o).sum(axis=1)
        return winnings.sum()

    def generate_summary(self, date):
        summary = {
            'Bankroll': self.bankroll,
            'Date': date,
            'Min_bet': self.min_bet,
            'Max_bet': self.max_bet,
        }
        return pd.Series(summary).to_frame().T

    def get_bets(self, summary: pd.DataFrame, inc: pd.DataFrame, opps: pd.DataFrame) -> pd.DataFrame:
        return self.interactor.place_bets(opps, summary, inc)

