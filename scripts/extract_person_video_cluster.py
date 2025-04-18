import sys
import os
import pandas as pd
from tqdm import tqdm

sys.path.append(".")
from scripts.extract_person_video import (
    confirm_folder,
    update_csv_path,
    pose_from_video,
)


def get_video_files_in_cluster(
    videos_folder_path: str, manual_include_word: str = None
) -> list:
    """Extract the videos from the cluster folders.

    Args:
        videos_folder_path (str):   Path to the folder containing cluster folders.
        manual_include_word (str):  Only include video files containing this word.

    Returns:
        list: List of video files in the cluster folders.
    """

    sub_dirs = [
        os.path.join(videos_folder_path, sub_dir)
        for sub_dir in os.listdir(videos_folder_path)
        if os.path.isdir(os.path.join(videos_folder_path, sub_dir))
    ]
    if len(sub_dirs) == 0:
        print(
            f"Error: No subdirectories found in the input folder '{videos_folder_path}'."
        )
        return []

    # Store video paths from sub_dirs
    video_paths = []
    for sub_dir in sub_dirs:

        sub_dir_name = os.path.basename(sub_dir)

        # Get video files in the subdirectory
        video_files = [
            os.path.join(sub_dir_name, video_file)
            for video_file in os.listdir(sub_dir)
            if video_file.lower().endswith((".mp4", ".avi", ".mov"))
            and (manual_include_word is None or manual_include_word in video_file)
        ]

        # Check if any video files were found
        if len(video_files) == 0:
            print(f"Error: No video files found in the input folder '{sub_dir}'.")
            continue

        # Add to the list of video paths
        video_paths.extend(video_files)

    return video_paths


def extract_person_from_videos(
    main_folder_path: str,
    output_folder: str = "data/labels/",
    videos_folder: str = "videos",
    manual_include_word: str = None,
    concat: bool = True,
) -> None:
    """Extracts people from folder of video clusters. Saves bounding boxes and tracking IDs to CSV file.

    Args:
        main_folder_path (str):     Path to the main folder containing cluster folders.
        output_folder (str):        Path to the output folder for CSV files.
        videos_folder (str):        Path to the folder containing video files.
        manual_include_word (str):  Only include video files containing this word.
        concat (bool):              Whether to concatenate CSV files or not.

    Returns:
        None: A new CSV file is created in the output folder. For each video if concat is False.
    """

    # Check if the main folder exists and is a directory
    videos_folder_path = confirm_folder(main_folder_path, videos_folder)

    relative_video_paths = get_video_files_in_cluster(
        videos_folder_path, manual_include_word
    )
    if len(relative_video_paths) == 0:
        print(f"Error: No video files found in the subdirectories.")
        return

    # Update CSV path
    concat_csv_path = update_csv_path(main_folder_path, output_folder, concat=concat)

    # Process each video file
    for relative_video_path in tqdm(relative_video_paths, desc="Videos"):

        # Run pose extraction
        video_path = os.path.join(videos_folder_path, relative_video_path)
        pose_from_video(video_path, concat_csv_path, concat=concat)


if __name__ == "__main__":

    # Add args
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract people from videos and save to CSV."
    )
    parser.add_argument(
        "--videos_folder",
        type=str,
        help="Path to the folder containing video files.",
        required=True,
    )
    parser.add_argument(
        "--output_folder",
        type=str,
        help="Path to the output folder for CSV files.",
        default="data/labels/",
    )
    parser.add_argument(
        "--manual_include_word",
        type=str,
        default=None,
        help="Only include video files containing this word.",
    )
    parser.add_argument(
        "--concat",
        action="store_true",
        help="Concatenate CSV files (default).",
        dest="concat",
    )
    parser.add_argument(
        "--no-concat", action="store_false", help="Individual CSV files.", dest="concat"
    )
    parser.set_defaults(concat=True)
    args = parser.parse_args()

    # Example usage
    """
    python scripts/extract_person_video.py --videos_folder "../data/conflict_acted_navigation_gestures" --output_folder "data/labels/" --no-concat --manual_include_word "front"
    """

    # Extract people from videos and save to CSV
    extract_person_from_videos(
        main_folder_path=args.videos_folder,
        output_folder=args.output_folder,
        videos_folder="videos",
        manual_include_word=args.manual_include_word,
        concat=args.concat,
    )
