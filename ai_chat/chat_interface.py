import os
import json
from typing import Any, Dict, List
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
import re


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

    def generate_transformations(self, user_input: str, columns: List[str]  ) -> List[Dict[str, Any]]:
        """
        Generates a sequence of transformation commands based on user input.
        """
        prompt_template = """
        You are a highly intelligent assistant that translates natural language instructions into a sequence of structured data transformation commands in JSON format. Each command should be a JSON object with a `command` field indicating the type of operation and a `parameters` field containing the details of that operation.

        ### Available Columns:
        {columns}

        ### Available Commands:
        1. **filter**:
           - Description: Filters rows in the data based on a condition.
           - Parameters:
             - `predicate`: A logical condition that rows must satisfy (e.g., "age > 30").
             - Example:
               ```json
               {{"command": "filter", "parameters": {{"predicate": "age > 30"}}}}
               ```

        2. **select**:
           - Description: Selects specific columns from the data.
           - Parameters:
             - `columns`: A list of column names to include.
             - Example:
               ```json
               {{"command": "select", "parameters": {{"columns": ["name", "age"]}}}}
               ```

        3. **add_column**:
           - Description: Adds a new column to the data based on a formula.
           - Parameters:
             - `column_name`: The name of the new column.
             - `formula`: A formula or expression to calculate the new column (e.g., "age / income").
             - Example:
               ```json
               {{"command": "add_column", "parameters": {{"column_name": "age_income_ratio", "formula": "age / income"}}}}
               ```

        ### Rules:
        1. Always return a JSON array containing the sequence of commands.
        2. Ensure the output strictly adheres to JSON formatting, including correct brackets, commas, and quotes.
        3. Interpret user input with precision and map it to the appropriate commands.
        4. Combine multiple instructions from the input into a single sequence of commands.
        5. Only use the available columns and commands provided in the prompt. Do not introduce new columns or commands.

        ### Examples:

        #### Example 1:
        **User Input:** "Filter rows where age > 30 and select the name and age columns."
        **Output:**
        ```json
        [
            {{"command": "filter", "parameters": {{"predicate": "age > 30"}}}},
            {{"command": "select", "parameters": {{"columns": ["name", "age"]}}}}
        ]
        ```

        #### Example 2:
        **User Input:** "Add a column named 'age_to_income_ratio' that divides age by income."
        **Output:**
        ```json
        [
            {{"command": "add_column", "parameters": {{"column_name": "age_to_income_ratio", "formula": "age / income"}}}}
        ]
        ```

        #### Example 3:
        **User Input:** "Filter rows where salary >= 50000, then add a column called 'tax' that calculates salary * 0.2, and finally select the name, salary, and tax columns."
        **Output:**
        ```json
        [
            {{"command": "filter", "parameters": {{"predicate": "salary >= 50000"}}}},
            {{"command": "add_column", "parameters": {{"column_name": "tax", "formula": "salary * 0.2"}}}},
            {{"command": "select", "parameters": {{"columns": ["name", "salary", "tax"]}}}}
        ]
        ```

        Now, translate the following user input into a sequence of commands:
        {input}
        """

        columns_list = ", ".join(columns)
        prompt_text = prompt_template.format(columns=columns_list, input=user_input)
        response = self.llm.invoke(prompt_text)
        response = sanitize_ai_response(response.content)

        try:
            transformations = json.loads(response)
            return transformations
        except json.JSONDecodeError:
            print("Error parsing the LLM response. Please ensure it is in JSON format.")
            return []
