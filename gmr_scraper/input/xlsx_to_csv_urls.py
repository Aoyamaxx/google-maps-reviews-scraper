import pandas as pd

# Function to extract coordinates from the URL
def extract_coordinates(url):
    try:
        coordinates_part = url.split('@')[1]
        coordinates = coordinates_part.split(',')[0:2]
        x_cor, y_cor = map(float, coordinates)
        return x_cor, y_cor
    except (IndexError, ValueError):
        return None, None

# Function to process the Excel file and generate the CSV
def process_excel_file(excel_path):
    df = pd.read_excel(excel_path)

    for index, row in df.iterrows():
        if pd.isna(row['X_Cor']) or pd.isna(row['Y_Cor']):
            x_cor, y_cor = extract_coordinates(row['URL'])
            if x_cor is not None and y_cor is not None:
                df.at[index, 'X_Cor'] = x_cor
                df.at[index, 'Y_Cor'] = y_cor

    output_csv_path = 'urls.csv'
    df.to_csv(output_csv_path, index=False)

    return output_csv_path

if __name__ == "__main__":
    excel_file_path = 'hand_written_urls.xlsx'
    output_csv_path = process_excel_file(excel_file_path)
    print(f"CSV file changed: {output_csv_path}")