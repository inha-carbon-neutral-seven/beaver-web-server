from enum import Enum
from typing import List, Union

from langchain.pydantic_v1 import BaseModel, Field


class ChartType(str, Enum):
    BAR = "bar"
    PIE = "pie"


class Series(BaseModel):
    name: str
    data: List[Union[int, float]]


class ChartOutput(BaseModel):
    title: str = Field(description="차트의 특성을 잘 표현하는 제목입니다. 한국어로 표현합니다.")
    series: List[Series] = Field(
        description="""List of series points for the chart,
each containing a name, type, and data points."""
    )
    labels: List[str] = Field(
        description="List of labels for the chart, providing context to the displayed data."
    )
    type: ChartType = Field(
        description="""The type of chart to be displayed on the dashboard.
It determines the overall layout and the way data is represented in the chart.

"bar" type will represent data in rectangular bars,
helpful for comparing quantities across categories.

"pie" type will represent data in sectors of a circle,
ideal for showing the proportion of parts against the whole."""
    )

    def to_dict(self):
        return {
            "title": self.title,
            "series": self.series,
            "labels": self.labels,
            "type": self.type,
        }
