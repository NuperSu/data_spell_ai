# Data Transformation Assistant

This project is a data transformation assistant that uses natural language input to generate and apply structured transformations on a Pandas DataFrame. It leverages OpenAI's GPT-based models to interpret instructions and execute transformations like filtering, selecting columns, and adding calculated columns.

---

## Features

- Accepts natural language instructions to transform data.
- Automatically generates transformation commands in a structured JSON format.
- Supports the following operations:
  - **Filter:** Filters rows based on a condition.
  - **Select:** Selects specific columns.
  - **Add Column:** Adds new calculated columns using expressions.
- Modular and extensible design for easy maintenance and scalability.

---

## Installation

### Prerequisites

- Python 3.12+
- A valid OpenAI API key

### Steps

1. Clone this repository:
   ```bash
   git clone https://github.com/NuperSu/dataspell_ai_chat.git
   cd your_project
   ```

2. Set up a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Rename `.env.example' file to `.env` in the project root and replace placeholder with your OpenAI API key

5. Run the application:
   ```bash
   python main.py
   ```

---

### Example

**Input:**
```
Filter rows where salary > 50000 and select the name and salary columns.
```

**Output:**
```plaintext
Original DataFrame:
      name  age  salary
0    Alice   25   50000
1      Bob   35   60000
2  Charlie   45   70000
3    David   28   52000

Generated Transformations:
[
    Command(command='filter', parameters={'predicate': 'salary > 50000'}),
    Command(command='select', parameters={'columns': ['name', 'salary']})
]

Transformed DataFrame:
      name  salary
1      Bob   60000
2  Charlie   70000
3    David   52000
```

---

## Modules

### ai_chat/chat_interface.py

- **Description:** Manages interaction with the OpenAI API.
- **Key Features:**
  - Generates transformation commands based on natural language input.
  - Uses `Pydantic` to validate LLM output against a predefined schema.

### ai_chat/prompt_template.py

- **Description:** Contains the LLM prompt template for generating transformations.

### transformations/commands.py

- **Description:** Implements individual transformation functions.
- **Functions:**
  - `filter_data`: Filters rows based on a condition.
  - `select_columns`: Selects specific columns.
  - `add_column`: Adds calculated columns.

### transformations/apply_transformations.py

- **Description:** Applies a sequence of transformations to a Pandas DataFrame.
