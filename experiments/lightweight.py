from kf_utils.pipe_ops import run_pipe, compile_pipe
import kfp.components as comp

def add(a: float, b: float) -> float:
    return a + b

add_op = comp.func_to_container_op(add)

from typing import NamedTuple


def my_divmod(dividend: float, divisor: float) -> NamedTuple('MyDivmodOutput',
                                                             [('quotient', float), ('remainder', float),
                                                              ('mlpipeline_ui_metadata', 'UI_metadata'),
                                                              ('mlpipeline_metrics', 'Metrics')]):
    '''Divides two numbers and calculate  the quotient and remainder'''

    # Imports inside a component function:
    import numpy as np

    # This function demonstrates how to use nested functions inside a component function:
    def divmod_helper(dividend, divisor):
        return np.divmod(dividend, divisor)

    (quotient, remainder) = divmod_helper(dividend, divisor)

    from tensorflow.python.lib.io import file_io
    import json

    # Exports a sample tensorboard:
    metadata = {
        'outputs': [{
            'type': 'tensorboard',
            'source': 'gs://ml-pipeline-dataset/tensorboard-train',
        }]
    }

    # Exports two sample metrics:
    metrics = {
        'metrics': [{
            'name': 'quotient',
            'numberValue': float(quotient),
        }, {
            'name': 'remainder',
            'numberValue': float(remainder),
        }]}

    from collections import namedtuple
    divmod_output = namedtuple('MyDivmodOutput',
                               ['quotient', 'remainder', 'mlpipeline_ui_metadata', 'mlpipeline_metrics'])
    return divmod_output(quotient, remainder, json.dumps(metadata), json.dumps(metrics))

my_divmod(100, 7)

divmod_op = comp.func_to_container_op(my_divmod, base_image='tensorflow/tensorflow:1.11.0-py3')

import kfp.dsl as dsl
@dsl.pipeline(
    name='calculation-pipeline',
    description='A toy pipeline that performs arithmetic calculations.'
)
def calc_pipeline(
        a='4.0',
        b='7.0',
        c='17.0',
):
    # Passing pipeline parameter and a constant value as operation arguments
    add_task = add_op(a, 4)  # Returns a dsl.ContainerOp class instance.

    # Passing a task output reference as operation arguments
    # For an operation with a single return value, the output reference can be accessed using `task.output` or `task.outputs['output_name']` syntax
    divmod_task = divmod_op(add_task.output, b)

    # For an operation with a multiple return values, the output references can be accessed using `task.outputs['output_name']` syntax
    result_task = add_op(divmod_task.outputs['quotient'], c)



#Specify pipeline argument values
arguments = {'a': '7.0', 'b': '8.0'}

#Submit a pipeline run
compile_pipe(calc_pipeline)
run_pipe(calc_pipeline, arguments)

