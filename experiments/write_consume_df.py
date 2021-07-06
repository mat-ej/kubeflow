def writedf(output_dataframe_path: OutputBinaryFile()):
    import pandas as pd
    import numpy as np
    df = pd.DataFrame(np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9]]),
                   columns=['a', 'b', 'c'])
    df.to_pickle(output_dataframe_path)


def readdf(dataframe_path: InputBinaryFile()): # The "text" input is untyped so that any data can be printed
    import pandas as pd
    # df = pd.DataFrame()
    df = pd.read_pickle(dataframe_path)
    print(df)

write_df_op = create_component_from_func(writedf, base_image='matejcvut/kubeflow-pod:0')
read_df_op = create_component_from_func(readdf, base_image='matejcvut/kubeflow-pod:0')

@dsl.pipeline(
    name="df pipeline",
    description="create dataframe, consume dataframe"
)
def df_pipeline():
    write_df_task = write_df_op()
    read_df_task = read_df_op(write_df_task.output)
