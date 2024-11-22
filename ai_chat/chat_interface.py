import os
import json
import re
from typing import Any, Dict, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field, ValidationError


# Define the schema for the transformation commands
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
        if api_key:
            os.environ["OPENAI_API_KEY"] = api_key
        self.llm = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")

        self.output_parser = PydanticOutputParser(pydantic_object=TransformationSequence)

    def generate_transformations(self, user_input: str, columns: List[str]) -> List[Dict[str, Any]]:
        """
        Generates a sequence of transformation commands based on user input and available columns.
        """
        prompt_template = """
        You are an assistant that translates user instructions into a sequence of structured data transformation commands in JSON format. Each command should be a JSON object with a `command` field indicating the type of operation and a `parameters` field containing the details of that operation.

        ### Available Columns:
        {columns}

        ### Available Commands:
        1. **filter**:
           - Description: Filters rows in the data based on a condition.
           - Parameters:
             - `predicate`: A logical condition that rows must satisfy (e.g., "age > 30").
             - Example:
               {{ "command": "filter", "parameters": {{ "predicate": "age > 30" }} }}

        2. **select**:
           - Description: Selects specific columns from the data.
           - Parameters:
             - `columns`: A list of column names to include.
             - Example:
               {{ "command": "select", "parameters": {{ "columns": ["name", "age"] }} }}

        3. **add_column**:
           - Description: Adds a new column to the data based on a formula.
           - Parameters:
             - `column_name`: The name of the new column.
             - `formula`: A formula or expression to calculate the new column (e.g., "age / income").
             - Example:
               {{ "command": "add_column", "parameters": {{ "column_name": "age_income_ratio", "formula": "age / income" }} }}

        ### Rules:
        1. Always return a JSON object containing a key `transformations`, which maps to an array of command objects.
        2. Ensure the output strictly adheres to the JSON schema defined for each command.
        3. Interpret user input with precision and map it to the appropriate commands.
        4. Combine multiple instructions from the input into a single sequence of commands.

        ### Examples:

        #### Example 1:
        **User Input:** "Filter rows where age > 30 and select the name and age columns."
        **Output:**
        ```json
        {{
            "transformations": [
                {{ "command": "filter", "parameters": {{ "predicate": "age > 30" }} }},
                {{ "command": "select", "parameters": {{ "columns": ["name", "age"] }} }}
            ]
        }}
        ```

        #### Example 2:
        **User Input:** "Add a column named 'age_to_income_ratio' that divides age by income."
        **Output:**
        ```json
        {{
            "transformations": [
                {{ "command": "add_column", "parameters": {{ "column_name": "age_to_income_ratio", "formula": "age / income" }} }}
            ]
        }}
        ```

        Now, translate the following user input into a sequence of commands:
        {input}
        """

        # Create a prompt template with both input and columns as variables
        prompt = PromptTemplate(
            input_variables=["input", "columns"],
            template=prompt_template
        )

        # Format the prompt with both input and columns
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
