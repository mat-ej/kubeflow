from kf_utils.env import *

def compile_pipe(pipeline) -> str:
    pipeline_path = PIPE_DIR + pipeline.__name__ + '.yaml'
    kfp.compiler.Compiler().compile(pipeline, pipeline_path)
    return pipeline_path


def run_pipe(pipeline, arguments = None, experiment_name = "Default"):
    return client.create_run_from_pipeline_func(pipeline, arguments=arguments, experiment_name=experiment_name)

def compile_run_pipe(pipeline, arguments = None, experiment_name = "Default"):
    pipe_local_path = compile_pipe(pipeline)
    run_result = run_pipe(pipeline, arguments, experiment_name)
    return (pipe_local_path, run_result)

