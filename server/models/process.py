from enum import Enum
from typing import List, Optional, Union

from langchain.pydantic_v1 import BaseModel, Field

from .chart import ChartOutput
from .recap import RecapOutput


class ProcessType(str, Enum):
    EMBED = "embed"
    RECAP = "recap"
    RECOMMENDATION = "recommendation"
    CHART = "chart"


class ProcessInput(BaseModel):
    type: ProcessType


class ProcessOutput(BaseModel):
    status: bool = Field(False)
    type: Optional[ProcessType] = Field(None)
    output: Union[RecapOutput, List[str], List[ChartOutput], None] = Field(None)
