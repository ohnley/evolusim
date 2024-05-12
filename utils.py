import pandas as pd
import random


def append_to_dataframe(actions_taken, epoch, df=None):
    # Define a mapping from tuples to directions
    direction_mapping = {
        (0, 1): 'down',
        (0, -1): 'up',
        (1, 0): 'right',
        (-1, 0): 'left'
    }

    # Flatten the dictionary
    flattened_data = {}
    for action, directions in actions_taken.items():
        for direction, value in directions.items():
            flattened_data[f"{action}_{direction_mapping[direction]}"] = value

    # Add the epoch variable to the flattened data
    flattened_data['epoch'] = epoch

    # Create a DataFrame from the flattened data
    new_df = pd.DataFrame([flattened_data])

    # Append the new DataFrame to the existing DataFrame (if provided)
    if df is None:
        df = new_df
    else:
        df = pd.concat([df, new_df], ignore_index=True)

    return df


def generate_unique_random_points(height, width, n):
    if n > height * width:
        raise ValueError(f"Cannot generate {n} unique points in a {height}x{width} grid.")

    all_points = [(x, y) for x in range(width) for y in range(height)]
    random.shuffle(all_points)
    return all_points[:n]