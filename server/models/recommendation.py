from typing import List

from langchain.pydantic_v1 import BaseModel, Field


class RecommendationOutput(BaseModel):
    """
    Data model for a Recommendation.
    """

    recommendations: List[str] = Field(
        description="""전체 맥락에서, 서로 다른 주제에 대해 물어보는 세 가지 질문 예시.
한국어 존댓말과 함께, 물음표로 된 질문문 형식을 지켜야 합니다. 반드시 3개여야 합니다. """
    )

    def to_dict(self):
        return {
            "recommendations": self.recommendations,
        }
