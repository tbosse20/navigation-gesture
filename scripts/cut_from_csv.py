import os
import sys
import pandas as pd
from tqdm import tqdm

sys.path.append(".")
from scripts.cut_video_cluster import cut_video_cluster


def cut_with_csv(csv_file: str):
    """Cut the videos in the JSON file, using the given information.

    Args:
        csv_file (str): Path to the CSV file containing video information.

    Returns:
        None: The function saves the cut videos in the specified output folder "_cut".
    """

    # Check if the JSON file exists
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"JSON file {csv_file} does not exist.")
    if not os.path.isfile(csv_file):
        raise NotADirectoryError(f"JSON file {csv_file} is not a file.")

    # Load the CSV file
    df = pd.read_csv(csv_file)
    # Check if the CSV file is empty
    if df.empty:
        raise ValueError(f"CSV file {csv_file} is empty.")
    # Check required columns
    required_columns = [
        "folder_path",
        "start_min",
        "start_sec",
        "end_min",
        "end_sec",
    ]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Column '{col}' is missing in the CSV file.")

    # Get the output folder name
    videos_folder_name = os.path.basename(os.path.normpath(os.path.dirname(csv_file)))

    # Create the output folder for cut videos
    main_dir = os.path.dirname(csv_file)
    sibling_main_dir = os.path.dirname(main_dir)
    output_folder = os.path.join(sibling_main_dir, videos_folder_name + "_cut")
    os.makedirs(output_folder, exist_ok=True)

    # Iterate through each video in the JSON file
    for index, video in tqdm(df.iterrows(), total=len(df), desc="Cutting videos"):
        folder_path = video["folder_path"]
        start_min = video["start_min"]
        start_sec = video["start_sec"]
        end_min = video["end_min"]
        end_sec = video["end_sec"]

        start_time = start_min * 60 + start_sec
        end_time = end_min * 60 + end_sec
        
        # Convert relative path to absolute path
        current_folder_path = os.path.join(main_dir, folder_path)

        # Ensure the start and end frame indices are valid
        if start_time < 0 or end_time < 0:
            print(f"Invalid frame indices for video {current_folder_path}. Skipping.")
            continue
        if start_time >= end_time:
            print(
                f"Start frame index '{start_time}' is greater than or equal to last frame index '{end_time}' for video '{folder_path}'. Skipping."
            )
            continue
        if not isinstance(start_time, (int)) or not isinstance(end_time, (int)):
            print(f"Frame indices must be integers for video {current_folder_path}. Skipping.")
            continue

        # Check if the video file exists
        if not os.path.exists(current_folder_path):
            print(f"Video file {current_folder_path} does not exist. Skipping.")
            continue
        
        is_dir = os.path.isdir(current_folder_path)
        
        # Set base of the output file name
        video_name = f"video_{index:02d}"
        # Convert to mp4 if not a directory
        video_name = video_name + ".mp4" if not is_dir else video_name
        # Create the output file path
        output_file_path = os.path.join(output_folder, video_name)
        
        # Check if the output file already exists
        if os.path.exists(output_file_path):
            print(f"Output file {output_file_path} already exists. Skipping.")
            continue
        
        # Create the output directory if it doesn't exist
        if is_dir:
            os.makedirs(output_file_path, exist_ok=True)
        print(f"Output file path: {output_file_path}")

        # Cut the video using the cut_video_time function
        cut_video_cluster(
            input_dir=current_folder_path,
            start_time=start_time,
            end_time=end_time,
            output_dir=output_file_path,
        )

        print(f"Cutting video: {folder_path} from {start_time}s to {end_time}s")

    print(f"Cut videos saved in: {output_folder}")


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        description="Cut videos using information from a CSV file."
    )
    parser.add_argument(
        "csv_file",
        type=str,
        help="Path to the CSV file containing video information.",
    )
    args = parser.parse_args()

    # Example usage:
    """ 
    python scripts/cut_from_csv.py \
        ../castle_svenmollytonkoross (rough)_concat.csv
    """

    cut_with_csv(args.csv_file)
