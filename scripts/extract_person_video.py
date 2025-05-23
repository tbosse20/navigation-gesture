import os
from tqdm import tqdm
from ultralytics import YOLO
import torch
import cv2
import logging
import numpy as np

# Suppress YOLOv8 logging
logging.getLogger("ultralytics").setLevel(logging.ERROR)


def update_csv_path(
    videos_folder_path: str, output_folder: str, concat: bool = False
) -> str:
    """Updates the CSV path based on the video folder and output folder.

    Args:
        videos_folder_path (str):   Path to the folder containing video files.
        output_folder (str):        Path to the output folder for CSV files.
        concat (bool):              Whether to concatenate CSV files or not.

    Returns:
        str: Updated CSV path.
    """

    # Get the output folder name
    videos_folder_name = os.path.basename(os.path.normpath(videos_folder_path))

    # Separate by adding the video folder name to the output folder
    if not concat:
        output_folder = os.path.join(output_folder, videos_folder_name)
    output_folder = os.path.join(output_folder, "unclean", "bbox")
    os.makedirs(output_folder, exist_ok=True)

    # Make initial CSV path
    csv_filename = (
        f"{videos_folder_name}_unclean_bbox.csv"
        if not concat
        else ".csv"
    )
    
    csv_path = os.path.join(output_folder, csv_filename)

    # Skip if individual CSV files are not needed and the file already exists
    if not concat or os.path.exists(csv_path):
        return csv_path

    # Make concatenated CSV file
    with open(csv_path, "w") as f:
        f.write("video_name,frame_id,pedestrian_id,x1,y1,x2,y2\n")

    return csv_path


def confirm_folder(main_folder_path: str, videos_folder: str = None) -> None:
    """Confirms the existence of the main folder and the video folder."""

    # Get the video folder path
    if not videos_folder is None:
        videos_folder_path = os.path.join(main_folder_path, videos_folder)

    # Check if the video folder exists and is a directory
    if not os.path.exists(videos_folder_path):
        raise FileNotFoundError(f"Video folder {videos_folder_path} does not exist.")
    if not os.path.isdir(videos_folder_path):
        raise NotADirectoryError(
            f"Video folder {videos_folder_path} is not a directory."
        )

    return videos_folder_path


def extract_person_from_videos(
    main_folder_path: str,
    output_folder: str = "data/labels/",
    concat: bool = True,
) -> None:
    """Extracts people from folder of videos. Saves bounding boxes and tracking IDs to CSV file.

    Args:
        videos_folder (str): Path to the folder containing video files.
        output_folder (str): Path to the output folder for CSV files.
        concat (bool):       Whether to concatenate CSV files or not.

    Returns:
        None: A new CSV file is created in the output folder.
    """

    # Check if the main folder exists and is a directory
    videos_folder_path = confirm_folder(main_folder_path)

    video_files = get_videos(videos_folder_path)
    if len(video_files) == 0:
        print(
            f"Error: No video files found in the input folder '{videos_folder_path}'."
        )
        return

    # Update CSV path
    concat_csv_path = update_csv_path(main_folder_path, output_folder, concat=concat)

    # Process each video file
    for video_file in tqdm(video_files, desc="Videos"):

        # Run pose extraction
        video_path = os.path.join(videos_folder_path, video_file)
        pose_from_video(video_path, concat_csv_path, concat=concat)


def get_videos(videos_folder_path: str) -> list:
    """Get video files from the main folder.

    Args:
        videos_folder_path (str): Path to the folder containing video files.

    Returns:
        list: List of video files.
    """
    # Get videos from the main folder
    relative_video_paths = [
        video_file
        for video_file in os.listdir(videos_folder_path)
        if video_file.endswith((".mp4", ".avi", ".mov", ".MP4"))
    ]
    # Return if any video files are found
    if len(relative_video_paths) > 0:
        return relative_video_paths

    # If no video files are found in subdirectories, return an empty list
    return []


def add_tqdm(element, video_path):

    # Get total frame count using OpenCV
    cap = cv2.VideoCapture(video_path)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()

    # Get video file name
    video_file = os.path.basename(video_path)

    # Initialize tqdm progress bar
    element = tqdm(element, total=total_frames, desc=video_file, unit="frames")

    return element


def pose_from_video(video_path: str, csv_path: str, concat: bool = False):
    """Extracts people from video and saves them with bounding boxes and tracking IDs in a CSV file."""

    # Check if the video file exists and is a valid format
    if not os.path.exists(video_path):
        print(f"Error: Video file {video_path} does not exist.")
        return
    if not os.path.isfile(video_path):
        print(f"Error: Video file {video_path} is not a file.")
        return
    if not video_path.endswith((".mp4", ".avi", ".mov", ".MP4")):
        print(f"Error: Video file {video_path} is not a valid video format.")
        return

    # Split directory and file name
    split_video_file = os.path.normpath(video_path).split(os.sep)
    video_name = split_video_file[-2]
    camera = split_video_file[-1].split(".")[0]

    # Convert to individual CSV file
    individual_csv_path = csv_path.replace(".csv", f"_{video_name}_{camera}.csv")
    # individual_csv_path = csv_path.replace(".csv", f"{video_name}_{camera}.csv") # Update to be contain path without all folders
    csv_path = csv_path if concat else individual_csv_path

    # Create individual CSV file for each video if it doesn't exist
    if not os.path.exists(csv_path) and not concat:
        with open(csv_path, "w") as f:
            f.write("video_name,camera,frame_id,pedestrian_id,x1,y1,x2,y2\n")
    else:
        return  # Skip if the file already exists and concatenation is not needed

    # Get existing lines from the CSV file to test for duplicates
    with open(csv_path, "r") as f:
        lines = f.readlines()

    # Load YOLO model
    yolo = YOLO("weights/yolov8s.pt")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    yolo.to(device).eval()

    # Track full video and stream frame-by-frame
    results = yolo.track(
        source=video_path,
        stream=True,
        persist=True,
        conf=0.1,
        iou=0.6,
    )

    # Process each frame and extract people
    results = add_tqdm(results, video_path)
    for frame_id, result in enumerate(results):
        if result.boxes is None:
            continue

        # Get video file name and dimensions
        width, height = result.orig_shape[1], result.orig_shape[0]

        # Skip if already in file
        if any(f"{video_name},{frame_id}" in line for line in lines):
            continue

        # Exclude non-person detections
        person_boxes = result.boxes[result.boxes.cls == 0]
        if len(person_boxes) == 0:
            continue

        # Process each detected person
        for box in person_boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            x1_norm, y1_norm, x2_norm, y2_norm = np.array([x1, y1, x2, y2]) / np.array(
                [width, height, width, height]
            )
            pedestrian_id = int(box.id[0]) if box.id is not None else -1

            # Append result to CSV
            with open(csv_path, "a") as f:
                f.write(
                    f"{video_name},{camera},{frame_id},{pedestrian_id},{x1_norm},{y1_norm},{x2_norm},{y2_norm}\n"
                )


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
        "--filter",
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
    python scripts/extract_person_video.py --videos_folder "../data/conflict_acted_navigation_gestures" --output_folder "data/labels/" --no-concat --filter "front"
    """

    # Extract people from videos and save to CSV
    extract_person_from_videos(
        main_folder_path=args.videos_folder,
        output_folder=args.output_folder,
        videos_folder="videos",
        filter=args.filter,
        concat=args.concat,
    )
