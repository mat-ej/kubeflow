import kfp
import kfp.dsl as dsl
import pandas as pd
import kfp.components as comp
from kfp.components import create_component_from_func

from kf_utils.pipe_ops import compile_pipe, run_pipe
from kf_utils.env import client

def read_csv(file_path):
    import pandas as pd
    df = pd.read_csv(file_path)
    print(df.head())

read_csv_op = comp.create_component_from_func(read_csv, base_image='matejcvut/kubeflow-pod:0')

def drive_download_op(drive_file_id: str, local_file_path: str) -> str:
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
          arguments=['wget --no-check-certificate "https://docs.google.com/uc?export=download&id=$0" -O "$1"', drive_file_id, local_file_path],
          # file_outputs = {'downloaded': local_file_path}
    )


@dsl.pipeline(
    name="download-drive-csv",
    description="download csv from drive and store into claimed pvc volume"
)
def download_drive_csv_to_volume_pipe(drive_file_id: str = '1oiudIrYHaxjW6sEVh_GH7YlIVT_Xi0Od',
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

    drive_download_task = drive_download_op(drive_file_id, local_file_path).add_pvolumes({volume_mnt_point : vop.volume})
    read_csv_task = read_csv_op(local_file_path).add_pvolumes({volume_mnt_point : drive_download_task.pvolume})
    # print(read_csv_task.outputs)
    # print(drive_download_task.output)

if __name__ == '__main__':
    pipeline_path = compile_pipe(download_drive_csv_to_volume_pipe)
    # client.upload_pipeline_version(pipeline_path, pipeline_name=download_drive_csv_to_volume_pipe.__name__, description="downloads csv from drive and stores into attached pvc volume")
    run_pipe(download_drive_csv_to_volume_pipe, experiment_name='soccer')
    #
    # print('etela')

    # dataflow_python_op = comp.load_component_from_url(
    # 'https://raw.githubusercontent.com/kubeflow/pipelines/1.7.0-alpha.1/components/gcp/dataflow/launch_python/component.yaml')
    # help(dataflow_python_op)
