import os
import re
from typing import Any, Dict, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, ValidationError

from .prompt_template import get_prompt_template


class Command(BaseModel):
    command: str = Field(..., description="The type of command (e.g., filter, select, add_column).")
    parameters: Dict[str, Any] = Field(..., description="Parameters required for the command.")


class TransformationSequence(BaseModel):
    transformations: List[Command] = Field(..., description="A list of transformation commands to be applied.")


def sanitize_ai_response(message: str) -> str:
    """
    Removes code fences and any leading/trailing whitespace from the AI response.
    """
    pattern = r"```(?:json)?\n?([\s\S]*?)```"
    match = re.search(pattern, message)
    if match:
        return match.group(1).strip()
    return message.strip()


class AIChatInterface:
    def __init__(self, api_key: str = None):
        self.llm = ChatOpenAI(temperature=0,
                              model_name="gpt-4o")

        self.output_parser = PydanticOutputParser(pydantic_object=TransformationSequence)

    def generate_transformations(self, user_input: str, columns: List[str]) -> List[Dict[str, Any]]:
        """
        Generates a sequence of transformation commands based on user input and available columns.
        """
        prompt_template = get_prompt_template()

        prompt = PromptTemplate(
            input_variables=["input", "columns"],
            template=prompt_template
        )

        columns_list = ", ".join(columns)
        prompt_text = prompt.format(input=user_input, columns=columns_list)

        # Invoke the LLM with the formatted prompt
        response = self.llm.invoke(prompt_text)
        sanitized_response = sanitize_ai_response(response.content)

        # Parse and validate the output using the structured schema
        try:
            result = self.output_parser.parse(sanitized_response)
            return result.transformations
        except ValidationError as e:
            print("Validation error in LLM output:")
            print(e)
            return []
