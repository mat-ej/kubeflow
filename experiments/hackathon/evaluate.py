import pandas as pd

import sys
sys.path.append(".")

from environment import Environment


# def run(self, season):
#     start = start if start is not None else self.dataset.Open.min()
#     end = end if end is not None else self.dataset.Date.max()
#
#     print(f"Start: {start}, End: {end}")
#     for date in pd.date_range(start, end):
#
#         opps = self.get_opps(date)
#         if opps.empty:
#             continue
#
#         inc = self.get_incremental_data(date)
#
#         placed = opps[self.bet_cols].sum().sum()
#
#         self.bankroll += self.evaluate_bets(inc)
#
#         summary = self.generate_summary(date)
#         print(
#             f'{date:%Y-%m-%d}: available: {self.bankroll:.2f}, invested {placed:.2f}, total {self.bankroll + placed:.2f}')
#
#         bets = self.get_bets(summary, inc, opps)
#
#         validated_bets = self.validate_bets(bets, opps)
#
#         self.place_bets(validated_bets)
#
#     self.bankroll += self.evaluate_bets(self.get_incremental_data(end + pd.to_timedelta(1, 'days')))
#
#     if hasattr(self.interactor, 'writeln'):
#         self.send_updates(pd.DataFrame(), pd.DataFrame(), pd.DataFrame())
#
#     return self.dataset

dataset = pd.read_csv('data/training_data.csv', parse_dates=['Date', 'Open'])
model = Model()
env = Environment(dataset, model, init_bankroll=1000., min_bet=5., max_bet=100.)
evaluation = env.run(start=pd.to_datetime('2005-07-01'))

print(f'Final bankroll: {env.bankroll:.2f}')

