import pandas as pd
from kf_utils.pipe_ops import compile_pipe, run_pipe
from kfp import components
from kfp.components import create_component_from_func
from precomponents import *

IMG = 'matejcvut/kubeflow-pod:0'
csv_to_pickle_op = create_component_from_func(func=csv_to_pickle, base_image=IMG)
names2ids_op = create_component_from_func(func=names2ids, base_image=IMG)
elo_op = create_component_from_func(func=elo, base_image=IMG)
lr_op = create_component_from_func(func=lr, base_image=IMG)
pandas_transform_op = create_component_from_func(func=pandas_transform, base_image=IMG)
get_seasons_op = create_component_from_func(func=get_seasons, base_image=IMG)


@components.create_component_from_func
def print_op(s: int):
    print(s)

@dsl.pipeline(
    name="sequential pipe",
    description="pass pickle files along"
)
def looping_pipe(drive_file_id: str = '1oiudIrYHaxjW6sEVh_GH7YlIVT_Xi0Od'):
    drive_download_task = drive_download_op(drive_file_id)
    csv_to_pickle_task = csv_to_pickle_op(input_csv_path=drive_download_task.output)
    names2ids_task = names2ids_op(input_pkl_path=csv_to_pickle_task.output)
    get_seasons_task = get_seasons_op(csv_to_pickle_task.output)

    with dsl.ParallelFor(get_seasons_task.output) as season:
        transform_code = "df = df[df['Sea'] == {}]"
        pandas_query_task = pandas_transform_op(names2ids_task.output, transform_code = transform_code, args = [season])
        elo_task = elo_op(pandas_query_task.output)
        lr_task = lr_op(elo_task.output)

if __name__ == '__main__':
    df = pd.read_csv('data/data.csv')
    # print(df)
    # df = pd.DataFrame()
    # print(df)
    # pipeline_path = compile_pipe(df_pipeline)
    # run_pipe(df_pipeline, experiment_name='soccer')
    #
    # arr = np.array([1,2,3])
    # print()

    pipeline_path = compile_pipe(looping_pipe)
    run_pipe(looping_pipe, experiment_name='soccer')

    # print('etela')