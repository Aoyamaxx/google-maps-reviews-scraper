import pandas as pd

filename = input("Enter the filename of the CSV: ")

try:
    df = pd.read_csv(filename, usecols=['Location', 'Status'])

    # Drop duplicate rows based on 'Location' to ensure uniqueness
    unique_locations = df.drop_duplicates(subset=['Location']).reset_index(drop=True)

    # Add an 'Order' column that indicates the order and the number of locations
    unique_locations.insert(0, 'Order', range(1, 1 + len(unique_locations)))

    print(unique_locations.to_markdown(index=False))
    
except Exception as e:
    print(f"An error occurred: {e}")
