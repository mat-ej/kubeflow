import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder


pred_cols = ['pH', 'pD', 'pA']
team_cols = ['HID', 'AID']
h_col, a_col = team_cols
res_cols = ['H', 'D', 'A']
lge_col = 'LID'
bets_cols = ['BetH', 'BetD', 'BetA']
odds_cols = ['OddsH', 'OddsD', 'OddsA']
import kfp


@kfp.dsl.graph_component
class Model:
    def __init__(self):
        self.seen = pd.Index([])
        self.hist = pd.DataFrame()
        self.model = LogisticRegression(multi_class='multinomial', solver='lbfgs')
        self.teams = set()

    def update(self, inc: pd.DataFrame):
        inc.Date = pd.to_datetime(inc.Date)
        self.hist = self.hist.append(inc)
        self.teams = set(self.hist[team_cols[0]]).union(set(self.hist[team_cols[1]]))
        #self.teams = self.teams.union(set(inc[team_cols[0]])).union(set(inc[team_cols[1]]))
        self.hist = self.hist[self.hist.Date > self.hist.Date.max() - pd.to_timedelta(365, 'days')]
        cats = list(sorted(set(self.teams)))
        self.encoder = OneHotEncoder(sparse=False, categories=[cats, cats])

    def place_bets(self, opps: pd.DataFrame, summary: pd.DataFrame, inc) -> pd.DataFrame:
        self.update(inc)

        summary = summary.iloc[0].to_dict()
        preds = []
        opps = opps.loc[opps.index.difference(self.seen)]
        self.seen = self.seen.union(opps.index)
        opps = opps[opps[h_col].isin(self.teams) & opps[a_col].isin(self.teams)]
        for lid in set(opps[lge_col]):
            lge_matches = self.hist[self.hist[lge_col] == lid]
            if lge_matches.empty:
                continue
            self.encoder.fit(lge_matches[team_cols])
            transformed = self.encoder.transform(lge_matches[team_cols])
            y = np.zeros(len(lge_matches))
            y[lge_matches.HSC == lge_matches.ASC] = 1
            y[lge_matches.HSC < lge_matches.ASC] = 2
            tdiff = pd.to_datetime(summary['Date']) - lge_matches.Date
            sample_weight = np.exp(-tdiff.dt.days*0.002)
            self.model.fit(transformed, y, sample_weight=sample_weight)
            lge_opps = opps[opps[lge_col] == lid]
            lge_preds = self.model.predict_proba(self.encoder.transform(lge_opps[team_cols]))
            preds.append(pd.DataFrame(index=lge_opps.index, data=lge_preds, columns=pred_cols))
        if not preds:
            return pd.DataFrame()
        preds = pd.concat(preds)
        ev = preds.values * opps.loc[preds.index, odds_cols].values - 1
        max_ev = np.argmax(ev, axis=1)
        bets = np.zeros_like(preds.values)
        bets[np.arange(preds.shape[0]), max_ev] = max(1, summary['Min_bet'])
        bets = pd.DataFrame(index=preds.index, data=bets, columns=bets_cols)
        return bets
