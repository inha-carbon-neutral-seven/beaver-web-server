import logging

from typing import TypeVar

from langchain.chains import LLMChain
from langchain.output_parsers import PydanticOutputParser
from langchain.pydantic_v1 import BaseModel
from langchain_core.exceptions import OutputParserException
from langchain_core.prompts import PromptTemplate
from langchain_openai.chat_models import ChatOpenAI


JSON_FORMATTING_TEMPLATE = """{format_instructions}

Format the text in JSON format according to the instructions:
```
{text}
```
"""

T = TypeVar("T", bound=BaseModel)


class FormattedPydanticOutputParser(PydanticOutputParser[T]):
    """
    Parse an output using a pydantic model.
    If the input text is not in perfect JSON format, it corrects it using LLM to JSON format.
    """

    def parse(self, text: str) -> T:
        """
        Parse an output using a Pydantic model.
        If the input text is not in perfect JSON format, it corrects it using LLM to JSON format.

        @Execution Time
        Low
        """

        try:
            return super().parse(text)

        except (OutputParserException, ValueError):
            logging.warning("Incorrect JSON format detected at PydanticLLMOutputParser: %s", text)
            corrected_text = self._correct_json_format(text)
            return super().parse(corrected_text)

    def _correct_json_format(self, json_like_text: str) -> str:
        """
        Correct the JSON-like text format using LLM.

        :param text: The input text to be corrected.
        :return: Corrected JSON-like text.
        """
        llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-0125")

        prompt = PromptTemplate(
            input_variables=["text"],
            template=JSON_FORMATTING_TEMPLATE,
            partial_variables={
                "format_instructions": super().get_format_instructions(),
            },
        )

        chain = LLMChain(llm=llm, prompt=prompt)
        result = chain.invoke({"text": json_like_text})

        output_text = result["text"]
        logging.info("Result of proofreading: %s", output_text)
        return output_text
