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

    def generate_transformations(self, user_input: str) -> List[Dict[str, Any]]:
        """
        Generates a sequence of transformation commands based on user input.
        """
        prompt_template = """You are an assistant that translates user instructions into a sequence of data transformation commands.
Each command should be a JSON object with the command name and its parameters.
Available commands:
- filter: Filters rows based on a condition
- select: Selects specific columns
- add_column: Adds a new calculated column

Example:
User Input: "Filter rows where age > 30 and select the name and age columns."
Output:
```json
[
    {{"command": "filter", "parameters": {{"predicate": "age }} 30"}}}},
    {{"command": "select", "parameters": {{"columns": ["name", "age"]}}}}
]
```

Now, translate the following user input into a sequence of commands:
{input}"""

        prompt = PromptTemplate(
            input_variables=["input"],
            template=prompt_template
        )
        prompt_text = prompt.format(input=user_input)
        response = self.llm.invoke(prompt_text)
        response = sanitize_ai_response(response.content)

        try:
            transformations = json.loads(response)
            return transformations
        except json.JSONDecodeError:
            print("Error parsing the LLM response. Please ensure it is in JSON format.")
            return []
