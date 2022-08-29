# Flytekit AWS Sagemaker Processing Plugin

PLugin to create and use SageMaker Processing jobs in Flyte workflows

This is a standalone plugin and has no dependency on the current `aws-sagemaker`,
nor does it require any backend configuration for Flyte. 


To install the plugin, add the following dependency in your `Pipfile`:

```bash
flytekitplugins-sagemakerprocessing = {version = "==0.0.0+master", index = ""}
```


Below is an example implementation of a sagemaker processing job
```python
from flytekit import workflow
from flytekitplugins.sagemakerprocessing.processing import (
    ProcessingJobResourceConfig,
    AppSpecification,
    OutputType,
    InputType,
    SagemakerProcessingJobTask,
    SagemakerProcessingJobConfig,
    ProcessingJobInput,
    ProcessingJobOutput,
)

job = SagemakerProcessingJobTask(
    name="sm-job",
    task_config=SagemakerProcessingJobConfig(
        processing_job_resource_config=ProcessingJobResourceConfig(
            instance_count=1,
            instance_type="ml.m5.xlarge",
            role="",
            image_uri="",
            volume_size_in_gb=30,
        ),
        app_specification=AppSpecification(
            container_arguments=[
                ...
                "--resize",
                "224",
            ],
            environment={"CURALATE_ENV": "prod"},
            container_entry_point=None,
        ),
    ),
    input_type=InputType.FILE,
    output_type=OutputType.DIRECTORY,
)

directory = job(
    inputs=[
        ProcessingJobInput(
            name="input_1",
            local_path="/opt/ml/processing/input",
            s3_uri="",
        )
    ],
    outputs=[
        ProcessingJobOutput(
            name="output_1",
            local_path="/opt/ml/processing/output",
            s3_uri="",
        )
    ],
)
```