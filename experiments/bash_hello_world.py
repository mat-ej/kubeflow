# Copyright 2019 The Kubeflow Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


#NOTE bash download
# fetch = kfp.dsl.ContainerOp(name='download',
#  image='busybox',
#  command=['sh', '-c'],
#  arguments=[
#  'sleep 1;'
#  'mkdir -p /tmp/data;'
#  'wget ' + data_url +
#  ' -O /tmp/data/results.csv'
#  ],
#  file_outputs={'downloaded': '/tmp/data'})

import kfp
from kfp import dsl
from kf_utils.pipe_ops import compile_pipe, run_pipe
def echo_op():
    return dsl.ContainerOp(
        name='echo',
        image='library/bash:4.4.23',
        command=['sh', '-c'],
        arguments=['echo "hello world"']
    )


@dsl.pipeline(
    name='my-first-pipeline',
    description='A hello world pipeline.'
)
def hello_world_pipeline():
    echo_task = echo_op()


if __name__ == '__main__':
    compile_pipe(hello_world_pipeline)
    run_pipe(hello_world_pipeline)