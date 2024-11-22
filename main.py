import pandas as pd
from transformations.commands import COMMANDS
from ai_chat.chat_interface import AIChatInterface
import os
from dotenv import load_dotenv  # Import load_dotenv


def apply_transformations(df: pd.DataFrame, transformations: list) -> pd.DataFrame:
    for transform in transformations:
        command = transform.get("command")
        params = transform.get("parameters", {})
        func = COMMANDS.get(command)
        if func:
            df = func(df, **params)
        else:
            print(f"Unknown command: {command}")
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
