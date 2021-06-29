## change workflow executor
https://argoproj.github.io/argo-workflows/workflow-executors/

- pns has a bug of container exiting too quickly, requires sleep(1) if error present
- docker has no bugs, requires root privilege for containers. 
- use docker

#### Possibly change pns to docker 
- `k edit configmap workflow-controller-configmap -n kubeflow`
- change containerRuntimeExecutor: docker to pns


# TODO
figure out what difference is kf V1 vs V2 pipelines
`kfp.Client(host=kfp_endpoint).create_run_from_pipeline_func(
    #     dir_pipeline,
    #     arguments={},
    #     mode=kfp.dsl.PipelineExecutionMode.V2_COMPATIBLE
    # )`




