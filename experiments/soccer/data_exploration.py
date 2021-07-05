import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression

class Names2Ids():
    def __init__(self, name_cols=["HT", "AT"], id_cols=["HID", "AID"]):
        self.id_cols = id_cols
        self.name_cols = name_cols
        self.id_map = {}

    def compute_features(self, data: pd.DataFrame) -> pd.DataFrame:
        series = []
        for namec, idc in zip(self.name_cols, self.id_cols):
            series.append(data[namec].map(self.id_map.get).rename(idc))
        return pd.concat(series, axis=1)

    def fit(self, data: pd.DataFrame):
        names = set.union(*[set(data[col]) for col in self.name_cols])
        self.id_map.update({name: id for id, name in enumerate(sorted(names))})


class EloTransformer():
    def __init__(self, k0, home_adv, gamma, ratings=None, c=10, d=400,
                 team_cols=['HID', 'AID'], score_cols=['HS', 'AS'], out_cols=['Elo_H', 'Elo_A']):
        self.score_cols = score_cols
        self.team_cols = team_cols
        self.out_cols = out_cols
        self.d = d
        self.c = c
        self.gamma = gamma
        self.home_adv = home_adv
        self.k0 = k0
        if ratings:
            self.ratings = ratings
            self.fitted = True
        else:
            self.fitted = False
            self.ratings = None

    def fit(self, dataset: pd.DataFrame):
        data = dataset[self.team_cols + self.score_cols].values
        self.ratings, _ = EloTransformer.compute_ratings(data, self.home_adv, self.k0, self.gamma, self.c, self.d)
        self.fitted = True
        return self

    def transform(self, dataset: pd.DataFrame) -> pd.DataFrame:
        assert self.fitted
        data = dataset[self.team_cols].values

        hids = data[:, 0]
        aids = data[:, 1]

        hrtgs = self.rating[hids]
        artgs = self.rating[aids]
        return pd.DataFrame(data=np.column_stack(hrtgs, artgs), columns=self.out_cols)

    @staticmethod
    def compute_ratings(data, HA, k0, gamma, c=10, d=400):

        N = data.shape[0]
        rtgs = np.zeros(np.max(data[:, :2]) + 1) + 1500
        hist = np.ones((N, 5))
        S = np.ones(N)
        S[data[:, 2] == data[:, 3]] = 0.5
        S[data[:, 2] < data[:, 3]] = 0

        for idx in range(N):
            HID, AID, HSC, ASC = data[idx]
            hrtg = rtgs[HID]
            artg = rtgs[AID]

            diff = hrtg - artg + HA
            E = 1 / (1 + c ** (-diff / d))

            k = k0 * ((1 + np.abs(HSC - ASC)) ** gamma)

            rtgs[HID] = hrtg + k * (S[idx] - E)
            rtgs[AID] = artg - k * (S[idx] - E)
            hist[idx] = hrtg, artg, rtgs[HID], rtgs[AID], E

        return rtgs, hist

    def fit_transform(self, df: pd.DataFrame):
        data = df[self.team_cols + self.score_cols].values
        self.ratings, hist = self.compute_ratings(data, self.home_adv, self.k0, self.gamma, self.c, self.d)
        self.fitted = True
        return pd.DataFrame(index=df.index, data=hist[:, :2], columns=self.out_cols)



df = pd.read_csv('data.csv')
# name_cols = ["HT", "AT"]
df = df[df.Sea == 2000]

n2id = Names2Ids()
n2id.fit(df)
df_id = n2id.compute_features(df)
df = df.join(df_id)

params = {  "k0": 10,
            "home_adv": 0,
            "gamma": 0,
            "score_cols": [
              "HS",
              "AS"
            ]}
elo_transf = EloTransformer(**params)

df_elo = elo_transf.fit_transform(df)
df = df.join(df_elo)

df_filtered = df[['HID', 'AID', 'Elo_H', 'Elo_A', 'WDL']]

model_params = {
            "multi_class": "multinomial",
            "solver": "lbfgs"
            }


features = df_filtered[['Elo_H', 'Elo_A']]
labels = df_filtered['WDL']


scikit_model = LogisticRegression(**model_params)
scikit_model.fit(features, labels.squeeze())
predictions = scikit_model.predict_proba(features)
print(predictions)