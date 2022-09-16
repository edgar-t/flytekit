import os
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, List, Dict, Optional

from dataclasses_json import dataclass_json
from sagemaker.processing import Processor, ProcessingInput, ProcessingOutput
from sagemaker.network import NetworkConfig

from flytekit import PythonInstanceTask
from flytekit import kwtypes
from flytekit.extend import Interface, TaskPlugins
from flytekit.types.directory import FlyteDirectory
from flytekit.types.file import FlyteFile


@dataclass_json
@dataclass
class OutputType(Enum):
    NONE = 1
    FILE = 2
    DIRECTORY = 3

@dataclass_json
@dataclass
class InputType(Enum):
    NONE = 1
    FILE = 2
    DIRECTORY = 3


@dataclass_json
@dataclass
class ProcessingJobInput(object):
    name: str
    local_path: str
    s3_uri: str


@dataclass_json
@dataclass
class ProcessingJobOutput(object):
    name: str
    local_path: str
    s3_uri: str


@dataclass_json
@dataclass
class ProcessingJobResourceConfig(object):
    instance_count: int
    instance_type: str
    role: str
    image_uri: str
    volume_size_in_gb: int
    max_runtime_in_seconds: Optional[int]
    in_curalate_vpc: bool

@dataclass_json
@dataclass
class AppSpecification(object):
    container_arguments: List[str]
    environment: Dict[str, str]
    container_entry_point: Any


@dataclass
class SagemakerProcessingJobConfig(object):
    processing_job_resource_config: ProcessingJobResourceConfig
    app_specification: AppSpecification


class SagemakerProcessingJobTask(PythonInstanceTask[SagemakerProcessingJobConfig]):
    _SAGEMAKER_PROCESSING_JOB_TASK = "sagemaker_processing_job_task"

    def __init__(
            self,
            name: str,
            task_config: SagemakerProcessingJobConfig,
            input_type: InputType = InputType.NONE,
            output_type: OutputType = OutputType.NONE,
            **kwargs
    ):
        self._task_config = task_config

        self.input_type = input_type

        if self.input_type is InputType.NONE:
            input_params = str
        else:
            input_params = List[ProcessingJobInput]

        self.output_type = output_type
        if self.output_type is OutputType.FILE:
            out_file = List[FlyteFile]
            output_params = List[ProcessingJobOutput]
        elif self.output_type is OutputType.DIRECTORY:
            out_file = FlyteDirectory
            output_params = List[ProcessingJobOutput]
        else:
            out_file = str
            output_params = str

        interface = Interface(
            inputs=kwtypes(inputs=input_params,
                           outputs=output_params),
            outputs=kwtypes(output_type=out_file),
        )

        super(SagemakerProcessingJobTask, self).__init__(
            name=name,
            task_config=task_config,
            task_type=self._SAGEMAKER_PROCESSING_JOB_TASK,
            interface=interface,
            **kwargs
        )

    def execute(self, **kwargs) -> Any:
        processor = Processor(
            role=self.task_config.processing_job_resource_config.role,
            image_uri=self.task_config.processing_job_resource_config.image_uri,
            instance_count=self.task_config.processing_job_resource_config.instance_count,
            instance_type=self.task_config.processing_job_resource_config.instance_type,
            volume_size_in_gb=self.task_config.processing_job_resource_config.volume_size_in_gb,
            entrypoint=None,
            env=self.task_config.app_specification.environment,
            max_runtime_in_seconds=self.task_config.processing_job_resource_config.max_runtime_in_seconds,
            network_config=NetworkConfig(enable_network_isolation=False,
                                         security_group_ids=["sg-2789ff41"],
                                         subnets=["subnet-027ebaf55db6b3d9b",
                                                  "subnet-62679914",
                                                  "subnet-e80111b1",
                                                  "subnet-085cda37990d2de62",
                                                  "subnet-a0fefd8b",
                                                  "subnet-600fbb5d"
                                                  ]) if self.task_config.processing_job_resource_config.in_curalate_vpc else None
        )
        job_inputs = [ProcessingInput(input_name=x.name, destination=x.local_path, source=x.s3_uri) for x in
                      kwargs.get("inputs")] if kwargs.get("inputs") and type(kwargs.get("inputs")) is not str else []
        job_outputs = [ProcessingOutput(output_name=x.name, destination=x.s3_uri, source=x.local_path) for x in
                       kwargs.get("outputs")] if kwargs.get("outputs") and type(kwargs.get("outputs")) is not str else []

        processor.run(
            job_name=self.name + "-" + datetime.now().strftime("%m-%d-%H-%M-%S"),
            inputs=job_inputs,
            outputs=job_outputs,
            arguments=self.task_config.app_specification.container_arguments,
            wait=True,
            logs=True
        )

        if self.output_type is OutputType.FILE:
            files = []
            for output in kwargs.get("outputs"):
                files.append(FlyteFile(output.s3_uri))
            return files
        elif self.output_type is OutputType.DIRECTORY:
            path, ext = os.path.splitext(kwargs.get("outputs")[0].s3_uri)
            if ext:
                path = os.path.dirname(path)
            return FlyteDirectory(path)
        else:
            return "Processing Job completed with no return value"


TaskPlugins.register_pythontask_plugin(SagemakerProcessingJobConfig, SagemakerProcessingJobTask)
