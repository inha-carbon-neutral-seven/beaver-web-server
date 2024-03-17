"""
POST /process
에 사용되는 비즈니스 로직을 담은 코드 페이지입니다.
"""

import logging

from typing import Any

import faiss

from langchain.pydantic_v1_core import ValidationError
from langchain_core.exceptions import OutputParserException
from llama_index import SimpleDirectoryReader, StorageContext, VectorStoreIndex
from llama_index.vector_stores.faiss import FaissVectorStore

from ..models.chart import ChartType
from ..models.process import ProcessOutput, ProcessType
from .chains.chart import generate_chart
from .chains.recap import generate_recap
from .chains.recommendation import generate_recommendation
from .ping import check_server_status
from .storage import get_document_path, get_vectorstore_path


def run(process_type: ProcessType, max_retries: int = 2) -> ProcessOutput:
    """
    임베딩 관련 서비스를 실행합니다.
    """
    status = False
    output: Any = None

    # 모델 서버가 불안정하면 임베딩을 진행하지 않습니다.
    if not check_server_status():
        return ProcessOutput(status=False)

    retries = 0
    while retries < max_retries:
        try:
            if process_type == ProcessType.EMBED:
                # 첨부한 파일을 임베딩합니다.
                if not _embed_document():
                    break

                status = True

            elif process_type == ProcessType.RECAP:
                output = generate_recap()

            elif process_type == ProcessType.CHART:
                # 첨부한 파일을 임베딩합니다.
                if not _embed_document():
                    break

                pie_chart_output = generate_chart(chart_type=ChartType.PIE)
                status = True

                if pie_chart_output is not None:
                    output = [pie_chart_output]

            elif process_type == ProcessType.RECOMMENDATION:
                recommendation_output = generate_recommendation()

                if recommendation_output is not None:
                    output = recommendation_output.recommendations

            else:
                output = None
                return ProcessOutput(status=False)

            # 에러 없이 성공했으므로 루프를 종료합니다.
            break

        except (OutputParserException, ValidationError, ValueError) as err:
            retries += 1
            logging.warning("OutputParserException iteration. [%s]", retries)

            # 최대 에러 횟수에 도달하면 실행을 종료합니다.
            if retries == max_retries:
                logging.warning("OutputParserException max iteration exceeded. \n%s", err)

                return ProcessOutput(status=False, type=process_type, output=output)

    if output is not None:
        status = True

    return ProcessOutput(status=status, type=process_type, output=output)


def _embed_document() -> bool:
    # dimensions of text-ada-embedding-002
    d = 1536
    faiss_index = faiss.IndexFlatL2(d)

    vector_store = FaissVectorStore(faiss_index=faiss_index)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    try:
        document_path = get_document_path()
        documents = SimpleDirectoryReader(document_path).load_data()

    except ValueError:  # 사용자로부터 파일을 받지 못했을 때 예외를 표출함
        return False

    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)

    # save index to disk
    vectorstore_path = get_vectorstore_path()
    index.storage_context.persist(persist_dir=vectorstore_path)
    return True
