import os
import sys
import pandas as pd
from tqdm import tqdm

sys.path.append(".")
from scripts.cut_video_cluster import cut_video_cluster


def handle_csv_file(csv_file: str) -> pd.DataFrame:
    """Handle the CSV file and check if it exists.

    Args:
        csv_file (str): Path to the CSV file.

    Returns:
        pd.DataFrame: DataFrame containing the CSV data.
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
    for column in required_columns:
        if column not in df.columns:
            raise ValueError(f"Missing required column '{column}' in CSV file.")

    return df


def handle_main_dir(csv_file: str) -> str:

    # Get the output folder name
    videos_folder_name = os.path.basename(os.path.normpath(os.path.dirname(csv_file)))

    # Create the output folder for cut videos
    main_dir = os.path.dirname(csv_file)
    sibling_main_dir = os.path.dirname(main_dir)
    output_folder = os.path.join(sibling_main_dir, videos_folder_name + "_cut")
    os.makedirs(output_folder, exist_ok=True)

    return main_dir, output_folder


def confirm_variables(
    input_folder_path: str,
    start_time_sec: int,
    end_time_sec: int,
    input_relative_folder_path: str,
) -> bool:
    """Check if the variables are valid.

    Args:
        current_folder_path (str): Path to the current folder.
        start_time_sec (int): Start time in seconds.
        end_time_sec (int): End time in seconds.
        folder_path (str): Path to the folder.

    Returns:
        bool: True if the variables are valid, False otherwise.
    """

    # Ensure the start and end frame indices are valid
    if start_time_sec < 0 or end_time_sec < 0:
        print(f"Invalid frame indices for video {input_folder_path}. Skipping.")
        return False

    if start_time_sec >= end_time_sec:
        print(
            f"Start frame index '{start_time_sec}' is greater than or equal to last frame index '{end_time_sec}' for video '{input_relative_folder_path}'. Skipping."
        )
        return False

    if not isinstance(start_time_sec, (int)) or not isinstance(end_time_sec, (int)):
        print(
            f"Frame indices must be integers for video {input_folder_path}. Skipping."
        )
        return False

    # Check if the video file exists
    if not os.path.exists(input_folder_path):
        print(f"Video file {input_folder_path} does not exist. Skipping.")
        return False

    return True


def handle_video_name(
    index: int,
    current_folder_path: str,
) -> str:
    """Handle the video name and output folder.

    Args:
        index (int): Index of the video.
        current_folder_path (str): Path to the current folder.
        output_folder (str): Path to the output folder.

    Returns:
        str: Name of the video file.
    """

    is_dir = os.path.isdir(current_folder_path)

    # Set base of the output file name
    video_name = f"video_{index:02d}"

    # Convert to mp4 if not a directory
    video_name = video_name + ".mp4" if not is_dir else video_name

    return video_name


def handle_output_file_path(
    video_name: str,
    output_folder: str,
    current_folder_path: str,
) -> str:
    """Handle the output file path.

    Args:
        video_name (str): Name of the video file.
        output_folder (str): Path to the output folder.
        current_folder_path (str): Path to the current folder.

    Returns:
        str: Path to the output file.
    """

    # Check if the current folder path is a directory
    is_dir = os.path.isdir(current_folder_path)

    # Create the output file path
    output_file_path = os.path.join(output_folder, video_name)

    # Check if the output file already exists
    if os.path.exists(output_file_path):
        print(f"Output file {output_file_path} already exists. Skipping.")
        return None

    # Create the output directory if it doesn't exist
    if is_dir:
        os.makedirs(output_file_path, exist_ok=True)

    return output_file_path


def cut_with_csv(csv_file: str):
    """Cut the videos in the JSON file, using the given information.

    Args:
        csv_file (str): Path to the CSV file containing video information.

    Returns:
        None: The function saves the cut videos in the specified output folder "_cut".
    """

    # Handle the CSV file
    df = handle_csv_file(csv_file)

    # Handle the main directory and output folder
    main_dir, output_folder = handle_main_dir(csv_file)

    # Initialize the start times CSV file
    start_times_csv_path, start_times_columns = init_start_time_csv(
        output_folder=output_folder,
    )

    # Iterate through each video in the JSON file
    for index, video in tqdm(df.iterrows(), total=len(df), desc="Cutting videos"):
        input_relative_folder_path = video[
            "folder_path"
        ]  # Relative path to the video folder from the CSV file
        start_min, start_sec = video["start_min"], video["start_sec"]
        end_min, end_sec = video["end_min"], video["end_sec"]

        # Convert start and end times to seconds
        start_time_sec = start_min * 60 + start_sec
        end_time_sec = end_min * 60 + end_sec

        # Convert relative path to absolute path
        input_folder_path = os.path.join(main_dir, input_relative_folder_path)

        if not confirm_variables(
            input_folder_path,
            start_time_sec,
            end_time_sec,
            input_relative_folder_path,
        ):
            continue

        video_name = handle_video_name(
            index,
            input_folder_path,
        )
        if video_name is None:
            continue

        output_file_path = handle_output_file_path(
            video_name,
            output_folder,
            input_folder_path,
        )
        if output_file_path is None:
            continue

        # Cut the video using the cut_video_time function
        cut_video_cluster(
            input_folder_path,
            start_time_sec,
            end_time_sec,
            output_file_path,
        )

        log_updated_real_start_time(
            video_name,
            input_relative_folder_path,
            start_time_sec,
            end_time_sec,
            start_times_csv_path,
            start_times_columns,
        )

    print(f"Cut videos saved in: {output_folder}")


def init_start_time_csv(
    output_folder: str,
):
    """Initialize the start times CSV file.
    Args:
        output_folder (str): Path to the output folder for cut videos.

    Returns:
        str: Path to the start times CSV file.
        list: List of columns for the start times CSV.
    """

    # Columns for the start times CSV
    start_times_columns = [
        "video_name",  # video name
        "start_datetime",  # start time in datetime format
        "duration_sec",  # duration in seconds
        "original_start_time",  # original start time in datetime format and video name
    ]

    # New csv containing the start times of each video
    start_times_csv_path = os.path.join(output_folder, "start_times.csv")

    # Make CSV to save the start times of each video
    if not os.path.exists(start_times_csv_path):
        os.makedirs(os.path.dirname(start_times_csv_path), exist_ok=True)
        pd.DataFrame(columns=start_times_columns).to_csv(
            start_times_csv_path, index=False
        )

    return start_times_csv_path, start_times_columns


def log_updated_real_start_time(
    video_name: str,
    input_relative_folder_path: str,
    start_time: int,
    end_time: int,
    start_times_csv_path: str,
    start_times_columns: list,
):
    """Log the updated real start time of the video in the CSV file.
    
    Args:
        video_name (str): Name of the video file.
        input_relative_folder_path (str): Relative path to the video folder from the CSV file.
        start_time (int): Start time in seconds.
        end_time (int): End time in seconds.
        start_times_csv_path (str): Path to the start times CSV file.
        start_times_columns (list): List of columns for the start times CSV.
        
    Returns:
        None: The function saves the updated real start time in the CSV file.
    """

    # Get start time from video name
    original_start_time_str = os.path.basename(input_relative_folder_path)
    # Convert time to datetime 2025-03-18_13-15-52
    original_start_time_dt = pd.to_datetime(
        original_start_time_str, format="%Y-%m-%d_%H-%M-%S"
    )
    # Add the start time to the original start time
    updated_real_start_time_dt = original_start_time_dt + pd.Timedelta(
        seconds=start_time
    )
    # Convert to string
    updated_real_start_time_str = updated_real_start_time_dt.strftime(
        "%Y-%m-%d_%H-%M-%S"
    )

    # Write new line to CSV with the video name and start time
    new_data = [
        [
            video_name,  # video name
            updated_real_start_time_str,  # start time in datetime format
            end_time - start_time,  # duration in seconds
            original_start_time_str,  # original start time in datetime format and video name
        ]
    ]
    pd.DataFrame(new_data, columns=start_times_columns).to_csv(
        start_times_csv_path, mode="a", header=False, index=False
    )


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
