import pandas as pd
from transformations.commands import COMMANDS
from ai_chat.chat_interface import AIChatInterface
import os
from dotenv import load_dotenv  # Import load_dotenv
from transformations.commands import filter_data, select_columns, add_column

def apply_transformations(df, transformations):
    for transform in transformations:
        # Access the command and parameters as attributes of the Command object
        command = transform.command
        parameters = transform.parameters

        if command == "filter":
            df = filter_data(df, **parameters)
        elif command == "select":
            df = select_columns(df, **parameters)
        elif command == "add_column":
            df = add_column(df, **parameters)
        else:
            raise ValueError(f"Unknown command: {command}")

    return df


def main():
    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found. Please set it in the .env file.")
        return

    ai_chat = AIChatInterface(api_key=api_key)

    # Sample DataFrame
    data = {
        "name": ["Alice", "Bob", "Charlie", "David"],
        "age": [25, 35, 45, 28],
        "salary": [50000, 60000, 70000, 52000]
    }
    df = pd.DataFrame(data)
    print("Original DataFrame:")
    print(df)

    user_input = input("Enter your data transformation instructions: ")

    transformations = ai_chat.generate_transformations(user_input, df.columns.tolist())
    print("\nGenerated Transformations:")
    print(transformations)

    transformed_df = apply_transformations(df, transformations)
    print("\nTransformed DataFrame:")
    print(transformed_df)


if __name__ == "__main__":
    main()
