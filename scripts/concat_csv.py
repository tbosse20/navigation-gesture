import os
import pandas as pd


def concat_csvs(csv_dir: str):
    """Concatenate all CSV files in a directory into a single CSV file.

    Args:
        csv_dir (str): Path to the directory containing CSV files.

    Returns:
        str: Path to the concatenated CSV file.
    """

    # Get all CSV files in the directory
    csv_files = [
        os.path.join(csv_dir, f) for f in os.listdir(csv_dir) if f.endswith(".csv")
    ]

    # Check if there are any CSV files to concatenate
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {csv_dir}.")

    # Concatenate the CSV files into a single DataFrame
    combined_df = pd.concat([pd.read_csv(f) for f in csv_files], ignore_index=True)

    # Save the combined DataFrame to a new CSV file
    combined_csv_path = os.path.join(csv_dir, "combined.csv")
    combined_df.to_csv(combined_csv_path, index=False)

    print(f"Combined CSV file saved at: {combined_csv_path}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Concatenate CSV files in a directory."
    )
    parser.add_argument(
        "--csv_dir",
        type=str,
        help="Path to the directory containing CSV files.",
        required=True,
    )
    args = parser.parse_args()

    # Example usage:
    """ 
    python concat_csv.py \
        --csv_dir ../data/actedgestures_original
    """

    # Call the function to concatenate CSV files
    combined_csv_path = concat_csvs(args.csv_dir)
