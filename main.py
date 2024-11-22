import pandas as pd
from transformations.apply_transformations import apply_transformations
from ai_chat.chat_interface import AIChatInterface
import os
from dotenv import load_dotenv


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
