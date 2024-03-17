from typing import List

from langchain.pydantic_v1 import BaseModel, Field


class RecapOutput(BaseModel):
    """
    Data model for a recap.
    """

    title: str = Field(description="제목, 문서의 주요 주제를 간결하게 한 줄로 요약합니다.")
    subtitle: str = Field(description="하위 제목, 하위 주제를 지정하며 추가 정보를 제공합니다.")
    summary: str = Field(description="문서 전체의 핵심 내용을 담은 길고 풍부한, 종합적인 서술입니다. ")
    keywords: List[str] = Field(
        description="키워드, 문서에서 자주 사용되는 중요한 단어나 용어 목록입니다.",
    )

    def to_dict(self):
        return {
            "title": self.title,
            "subtitle": self.subtitle,
            "summary": self.summary,
            "keywords": self.keywords,
        }
