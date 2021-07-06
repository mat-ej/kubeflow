# kubeflow
kf on prem 

# Setup notes 
## Port forward
### Pipelines UI
kubectl port-forward -n kubeflow svc/ml-pipeline-ui 8080:80
### Minio-service 
kubectl port-forward -n kubeflow svc/minio-service 9000:9000

## change workflow executor
https://argoproj.github.io/argo-workflows/workflow-executors/

- pns has a bug of container exiting too quickly, requires sleep(1) if error present
- docker has no bugs, requires root privilege for containers. 
- **use docker for now**

#### Possibly change pns to docker 
- `k edit configmap workflow-controller-configmap -n kubeflow`
- change containerRuntimeExecutor: docker to pns


# TODO
## figure out compilation time vs execution time variables:
    def drive_download_op(drive_file_id: str, output_csv_path: OutputTextFile(str)):
    '''
    :param drive_file_id:
    :param local_file_path:
    :return: bash container operation
    '''
    # print(output_csv_path)
    #TODO figure out file_outputs with a output_csv_path parameter instead of static string
    return dsl.ContainerOp(
          name='google drive download',
          image='library/bash:4.4.23',
          command=['sh', '-c'],
          arguments=['wget --no-check-certificate "https://docs.google.com/uc?export=download&id=$0" -O "$1"', drive_file_id, output_csv_path],
          file_outputs = {'downloaded': '/data/data.csv'}
    )

## figure out difference between kf V1 vs V2 pipelines
    kfp.Client(host=kfp_endpoint).create_run_from_pipeline_func(
        dir_pipeline,
        arguments={},
        mode=kfp.dsl.PipelineExecutionMode.V2_COMPATIBLE
    )








