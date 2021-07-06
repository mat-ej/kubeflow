from kf_utils.pipe_ops import compile_run_pipe, compile_pipe
from kfp.components import create_component_from_func, func_to_container_op
from precomponents import *

IMG = 'matejcvut/kubeflow-pod:0'
csv_to_pickle_op = create_component_from_func(func=csv_to_pickle, base_image=IMG)
names2ids_op = create_component_from_func(func=names2ids, base_image=IMG)
elo_op = create_component_from_func(func=elo, base_image=IMG)
lr_op = create_component_from_func(func=lr, base_image=IMG)
pandas_transform_op = create_component_from_func(func=pandas_transform, base_image=IMG)
get_seasons_op = create_component_from_func(func=get_seasons, base_image=IMG)

@func_to_container_op
def min_op(l: list) -> int:
    return min(l)

@func_to_container_op
def max_op(l: list) -> int:
    return max(l)

@func_to_container_op
def add_one_op(x: int) -> int:
    return x + 1

@dsl.graph_component
def training_loop(data, current_season: int = -1, max_season: int = -1):
    with dsl.Condition(current_season <= max_season):
        pandas_query_task = pandas_transform_op(data, transform_code="df = df[df['Sea'] == {}]", args=[current_season])
        elo_task = elo_op(pandas_query_task.output)
        lr_task = lr_op(elo_task.output)
        current_season = add_one_op(current_season).output
        training_loop(data, current_season, max_season)

@dsl.pipeline(
    name="recursive soccer pipe",
    description="recursively train on season by season"
)
def recursive_pipe(drive_file_id: str = '1oiudIrYHaxjW6sEVh_GH7YlIVT_Xi0Od'):
    drive_download_task = drive_download_op(drive_file_id)
    csv_to_pickle_task = csv_to_pickle_op(input_csv_path=drive_download_task.output)
    names2ids_task = names2ids_op(input_pkl_path=csv_to_pickle_task.output)
    get_seasons_task = get_seasons_op(csv_to_pickle_task.output)
    min_season = min_op(get_seasons_task.output).output
    max_season = max_op(get_seasons_task.output).output
    training_loop(data=names2ids_task.output, current_season=min_season, max_season=max_season)


if __name__ == '__main__':
    arguments = {'drive_file_id' : '1oiudIrYHaxjW6sEVh_GH7YlIVT_Xi0Od'}
    # compile_pipe(recursive_pipe)
    compile_run_pipe(recursive_pipe, arguments=arguments, experiment_name="soccer")