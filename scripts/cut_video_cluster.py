# %% Cut all videos in a folder by time
import os
import sys
from tqdm import tqdm

sys.path.append(".")
from scripts.cut_video_time import cut_video_time


def cut_video_cluster(input_dir: str, start_time: str, end_time: str, output_dir: str = None) -> None:
    """Cut video cluster by common word with time.
    
    Args:
        input_dir   (str): Path to the input video folder.
        start_time  (str): Start time in seconds.
        end_time    (str): End time in seconds.
        output_dir  (str): Path to the output folder.
        If None, it will be created in a sibling folder of the input folder.
    
    Returns:
        None: A new video file is created in a sibling folder of the input folder.
    
    """

    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Input folder '{input_dir}' not found.")
    if not os.path.isdir(input_dir):
        raise NotADirectoryError(f"'{input_dir}' is not a folder.")

    if output_dir is None:
        # Make new folder as sibling of input files parent folder
        output_dir = os.path.dirname(input_dir) + "_cut"
        os.makedirs(output_dir, exist_ok=True)

    # Get all files in the folder
    video_files = [
        video_file
        for video_file in os.listdir(input_dir)
        if video_file.endswith((".mp4", ".avi", ".mov", ".MP4"))
    ]
    
    for video_file in tqdm(video_files, desc="Cutting"):
        input_file = os.path.join(input_dir, video_file)

        # Create output folder as sibling of input files parent folder
        output_file = os.path.join(output_dir, os.path.basename(input_file))
        # Check if output file already exists
        if os.path.exists(output_file):
            raise FileExistsError(f"Output file '{output_file}' already exists.")

        cut_video_time(
            input_file=input_file,
            start_time=start_time,
            end_time=end_time,
            output_file=output_file,
        )


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(description="Cut video cluster.")
    parser.add_argument("--input_dir", type=str, help="Path to the input video folder.")
    parser.add_argument("--start_time", type=str, help="Start time in seconds.")
    parser.add_argument("--end_time", type=str, help="End time in seconds.")
    args = parser.parse_args()

    # Example usage
    """
    python cut_video_cluster.py \
        --input_dir  = "../data/actedgestures_original" \
        --start_time = 1 * 60 + 30 \
        --end_time   = 1 * 60 + 40
    """

    cut_video_cluster(
        input_dir="C:/Users/Tonko/OneDrive/Dokumenter/School/Merced/reconstruction/MVI_0050",
        start_time=1 * 60 + 30,  # Min * 60 + Sec
        end_time=1 * 60 + 40,  # Min * 60 + Sec
    )
