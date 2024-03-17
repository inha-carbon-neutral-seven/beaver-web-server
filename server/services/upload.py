"""
POST /upload
에 사용되는 비즈니스 로직을 담은 코드 페이지입니다.
"""

import numpy as np

from langchain.pydantic_v1 import BaseModel
from pandas import DataFrame

from .storage import clear_storage, load_dataframe, save_file


class DatetimeRange(BaseModel):
    column_name: str
    min: str
    max: str


def upload_file(contents: bytes, filename: str, description: str) -> dict:
    """
    클라이언트로부터 전달받은 파일을 웹 서버에 저장합니다
    """

    # 저장소를 초기화하고 파일을 저장합니다.
    clear_storage()
    save_file(contents, filename, description)

    # 테이블 데이터면 documentation을 추가로 생성합니다.
    df = load_dataframe()
    if isinstance(df, DataFrame):
        save_table_documentation(table_name=description, df=df)

    return {"filename": filename, "description": description}


def save_table_documentation(table_name: str, df: DataFrame):
    """
    테이블을 설명하는 documentation을 만들어 텍스트 문서로 저장합니다.
    """
    datetime_ranges = get_datetime_ranges(df=df)

    documentation = f"""
# '{table_name}' 테이블 데이터 분석

## 중요: 테이블 내용 요약
- 이 테이블은 소매업자가 첨부한 데이터입니다.
- {len(df)}개의 행과 {len(df.columns)}개의 열을 가지고 있습니다.
- 테이블의 첫 5행 내용을 확인하여 문서의 흐름을 이해할 수 있습니다:
{df.head().to_string()}

## 중요: 테이블 열 유형 분석
- 문서를 요약하거나 질문을 생성할 때 꼭 필요한 열 정보입니다.
- 테이블에 서술된 열들의 유형은 아래와 같습니다. 필요한 키워드를 파싱할 수 있습니다:
{df.dtypes.to_string()}

"""
    # datetime 열 추가 설명
    for datetime_range in datetime_ranges:
        documentation += f"## datetime '{datetime_range.column_name}' 추가 설명\n"
        documentation += f"- {datetime_range.min} 부터 {datetime_range.max} 까지의 날짜 범위를 가집니다.\n\n"

    # df.descibe() 통계 제공
    documentation += "## 참고자료: 테이블 정수 자료 분석\n"
    documentation += "- 데이터 분석할 때 참고할 수 있는 자료입니다.\n"

    for column in df.columns:
        if not df[column].dtype in [int, float]:
            continue

        documentation += f"- '{column}'에 대한 요약 통계\n: "

        for key, value in df[column].describe().items():
            documentation += f"{column}의 {key}: {value}, "
        documentation += "\n\n"

    # documentation 저장
    contents = documentation.encode(encoding="utf-8")
    description = f"{table_name}-documentation"
    save_file(contents=contents, filename="docs.txt", description=description)


def get_datetime_ranges(df: DataFrame) -> list[DatetimeRange]:
    """
    datetime type의 열들의 min date와 max date를 제공합니다.
    """
    datetime_ranges = []
    datetime_columns = df.select_dtypes(include=[np.datetime64])

    # datetime 열의 min, max date를 저장
    for column in datetime_columns.columns:
        datetime_range = DatetimeRange(
            column_name=column,
            min=str(df[column].min()),
            max=str(df[column].max()),
        )
        datetime_ranges.append(datetime_range)

    return datetime_ranges
