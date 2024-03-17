from langchain.pydantic_v1 import BaseModel, Field


# 서버 상태를 확인할 때 사용하는 모델
class Pong(BaseModel):
    status: bool = Field(description="서버 상태에 대한 bool 결과값입니다. ")
