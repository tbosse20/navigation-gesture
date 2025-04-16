import os
import json
import sys
sys.path.append(".")
from src.cut_video_time import cut_video_time

def cut_with_json(json_file: str):
    """Cut the videos in the JSON file, using the given information.

    Args:
        json_file (str): Path to the JSON file containing video information.

    Returns:
        None: The function saves the cut videos in the specified output folder "_cut".
    """

    # Check if the JSON file exists
    if not os.path.exists(json_file):
        raise FileNotFoundError(f"JSON file {json_file} does not exist.")
    if not os.path.isfile(json_file):
        raise NotADirectoryError(f"JSON file {json_file} is not a file.")

    # Load the JSON file
    with open(json_file, "r") as f:
        video_info = json.load(f)

    # Get the output folder name
    videos_folder_name = os.path.basename(os.path.normpath(os.path.dirname(json_file)))

    # Create the output folder for cut videos
    output_folder = os.path.join(
        os.path.dirname(json_file), videos_folder_name + "_cut"
    )
    os.makedirs(output_folder, exist_ok=True)

    # Iterate through each video in the JSON file
    for video in video_info:
        target_video = video["target_video"]
        video_path = video["video_path"]
        start_frame_index = video["start_frame_index"]
        last_frame_index = video["last_frame_index"]

        # Check if the video file exists
        if not os.path.exists(video_path):
            print(f"Video file {video_path} does not exist. Skipping.")
            continue

        # Get the output file name and path
        output_file_path = os.path.join(output_folder, target_video)

        cut_video_time(
            input_file=video_path,
            output_file=output_file_path,
            start_time=start_frame_index,
            duration=last_frame_index - start_frame_index,
        )

        print(
            f"Cutting video: {video_path} from {start_frame_index}s to {last_frame_index}s"
        )

    print(f"Cut videos saved in: {output_folder}")


if __name__ == "__main__":

    import argparse

    parser = argparse.ArgumentParser(
        description="Cut videos using information from a JSON file."
    )
    parser.add_argument(
        "json_file",
        type=str,
        help="Path to the JSON file containing video information.",
    )
    args = parser.parse_args()

    cut_with_json(args.json_file)
