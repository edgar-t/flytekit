"""
.. currentmodule:: flytekitplugins.sagemakerprocessing

This package contains things that are useful when extending Flytekit.

.. autosummary::
   :template: custom.rst
   :toctree: generated/

    SagemakerProcessingJobTask
    SagemakerProcessingJobConfig
    ProcessingJobInput
    ProcessingJobOutput
    AppSpecification
    OutputType
    InputType
    ProcessingJobResourceConfig
"""

__all__ = [
    "SagemakerProcessingJobTask",
    "SagemakerProcessingJobConfig",
    "ProcessingJobInput",
    "ProcessingJobOutput",
    "AppSpecification",
    "OutputType",
    "InputType",
    "ProcessingJobResourceConfig",

]

from .processing import SagemakerProcessingJobTask
from .processing import OutputType, InputType, ProcessingJobInput, ProcessingJobOutput, AppSpecification
from .processing import ProcessingJobResourceConfig, SagemakerProcessingJobConfig
