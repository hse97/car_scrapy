import pandas as pd
import os

def combine_csvs(input_folder, output_folder):
    # List to hold the dataframes
    dataframes = []

    # Loop through all files in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.csv'):
            file_path = os.path.join(input_folder, filename)
            # Read the CSV file
            df = pd.read_csv(file_path)
            # Append the dataframe to the list
            dataframes.append(df)

    # Concatenate all dataframes
    combined_df = pd.concat(dataframes, ignore_index=True)

    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Define the output file path
    output_file = os.path.join(output_folder, 'combined_csv.csv')

    # Save the combined dataframe to a new CSV file
    combined_df.to_csv(output_file, index=False)
    print(f"Combined CSV saved to {output_file}")

if __name__ == "__main__":
    # Folder containing the CSV files
    input_folder = '/home/alibi/Documents/Python/Car Tracker/auction_csvs'  # Change this to the path of your folder containing CSV files

    # Output folder
    output_folder = '/home/alibi/Documents/Python/Car Tracker/combined_data'

    # Combine the CSV files
    combine_csvs(input_folder, output_folder)
