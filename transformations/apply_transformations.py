from transformations.commands import filter_data, select_columns, add_column


def apply_transformations(df, transformations):
    for transform in transformations:
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
