import kfp
import kfp.dsl as dsl
import pandas as pd
from kfp.components import create_component_from_func

from kfp import components
from kf_utils.pipe_ops import compile_pipe, run_pipe
from kf_utils.env import client
# from kfp.components import func_to_container_op, InputPath, OutputPath
from kfp.components import InputPath, InputTextFile, OutputPath, OutputTextFile, func_to_container_op, OutputBinaryFile, InputBinaryFile


pandas_transform_csv_op = components.load_component_from_url('https://raw.githubusercontent.com/kubeflow/pipelines/6162d55998b176b50267d351241100bb0ee715bc/components/pandas/Transform_DataFrame/in_CSV_format/component.yaml')


def drive_download_op(drive_file_id: str, output_csv_path: OutputTextFile(str)):
    '''
    :param drive_file_id:
    :param local_file_path:
    # calls inside separate bash container wget --no-check-certificate  'https://docs.google.com/uc?export=download&id=1oiudIrYHaxjW6sEVh_GH7YlIVT_Xi0Od' -O 'data.csv'
    # NOTE no need to anotate, it already returns op directly
    :return: bash container operation
    '''
    return dsl.ContainerOp(
          name='google drive download',
          image='library/bash:4.4.23',
          command=['sh', '-c'],
          arguments=['wget --no-check-certificate "https://docs.google.com/uc?export=download&id=$0" -O "$1"', drive_file_id, output_csv_path],
          file_outputs = {'downloaded': '/data/isdb.csv'}
    )

def csv_to_pickle(input_csv_path: InputTextFile(), output_pkl_path: OutputBinaryFile()):
    import pandas as pd
    df = pd.read_csv(input_csv_path)
    df.to_pickle(output_pkl_path)

# source_file: InputTextFile(str), odd_lines_file: OutputTextFile(str), even_lines_file: OutputTextFile(str)
def names2ids(input_pkl_path: InputBinaryFile(), output_pkl_path: OutputBinaryFile()):
    import numpy as np
    import pandas as pd
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

    df = pd.read_pickle(input_pkl_path)
    n2id = Names2Ids()
    n2id.fit(df)
    df_id = n2id.compute_features(df)
    df = df.join(df_id)
    df.to_pickle(output_pkl_path)

def elo(input_pkl_path: InputBinaryFile(), output_pkl_path: OutputBinaryFile()):
    import pandas as pd
    import numpy as np
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


    params = {  "k0": 10,
        "home_adv": 0,
        "gamma": 0,
        "score_cols": [
          "HS",
          "AS"
        ]}
    elo_transf = EloTransformer(**params)

    df = pd.read_pickle(input_pkl_path)
    df_elo = elo_transf.fit_transform(df)
    df = df.join(df_elo)
    print(df.columns)
    df.to_pickle(output_pkl_path)


def lr(input_pkl_path: InputBinaryFile(), output_pkl_path: OutputBinaryFile()):
    import pandas as pd
    from sklearn.linear_model import LogisticRegression
    import pickle

    model_params = {
                "multi_class": "multinomial",
                "solver": "lbfgs"
                }


    df = pd.read_pickle(input_pkl_path)
    features = df[['Elo_H', 'Elo_A']]
    labels = df['WDL']


    scikit_model = LogisticRegression(**model_params)
    scikit_model.fit(features, labels.squeeze())
    predictions = scikit_model.predict_proba(features)
    print(predictions)
    pickle.dump(scikit_model, output_pkl_path)



csv_to_pickle_op = create_component_from_func(func=csv_to_pickle, base_image='matejcvut/kubeflow-pod:0')
names2ids_op = create_component_from_func(func=names2ids, base_image='matejcvut/kubeflow-pod:0')
elo_op = create_component_from_func(func=elo, base_image='matejcvut/kubeflow-pod:0')
lr_op = create_component_from_func(func=lr, base_image='matejcvut/kubeflow-pod:0')

@dsl.pipeline(
    name="sequential pipe",
    description="pass pickle files along"
)
def sequential_pipe(drive_file_id: str = '1oiudIrYHaxjW6sEVh_GH7YlIVT_Xi0Od',
                    local_file_path ='/data/isdb.csv',
                    volume_size: str = "1Gi",
                    volume_mnt_point: str = "/data"
                    ):

    vop = dsl.VolumeOp(
        name="create-pvc",
        resource_name="my-pvc",
        modes=dsl.VOLUME_MODE_RWM,
        size=volume_size
    )

    # drive_download_task = drive_download_op(drive_file_id, local_file_path).add_pvolumes({volume_mnt_point : vop.volume})
    # names2ids_task = names2ids_op(input_csv_path=local_file_path).add_pvolumes({volume_mnt_point : drive_download_task.pvolume})
    # print(names2ids_task)

    drive_download_task = drive_download_op(drive_file_id, local_file_path).add_pvolumes({volume_mnt_point : vop.volume})
    csv_to_pickle_task = csv_to_pickle_op(input_csv_path=drive_download_task.output)
    names2ids_task = names2ids_op(input_pkl_path=csv_to_pickle_task.output)
    elo_task = elo_op(names2ids_task.output)
    lr_task = lr_op(elo_task.output)

if __name__ == '__main__':
    # df = pd.DataFrame()
    # print(df)
    # pipeline_path = compile_pipe(df_pipeline)
    # run_pipe(df_pipeline, experiment_name='soccer')

    pipeline_path = compile_pipe(sequential_pipe)
    run_pipe(sequential_pipe, experiment_name='soccer')

    print('etela')