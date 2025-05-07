import os
import sys
import pandas as pd

sys.path.append(".")
import src.visualize_video_bbox as visualize_video_bbox


def main(video_path: str, bbox_csv: str = None, sequence_csv: str = None):
    """Visualize the video with bounding boxes and labels. Works only on clusters.

    Args:
        --video_path   (str):  Name of the video clip and camera name.
        --bbox_csv     (str):  Path to the CSV file containing bounding box data.
        --sequence_csv (str):  Path to the CSV file containing sequence data.

    Controls:
        - Space:        Play/Pause
        - Up Arrow:     Increase playback
        - Down Arrow:   Decrease playback
        - Left Arrow:   Backward 10 frames
        - Right Arrow:  Forward 10 frames
        - 'h':          Toggle HUD
        - 'q':          Quit

    Raises:
        FileNotFoundError:  If the video file does not exist.
        ValueError:         If the video format is not supported.
        ValueError:         If the CSV files are empty.

    Returns:
        None: Only visualizes the video with bounding boxes and labels.
    """
    
    # Get the video path
    # video_path = visualize_video_bbox.get_video_path(main_folder_path, video_name)

    # # Get the CSV files for the video
    # bbox_df, sequence_df = visualize_video_bbox.get_dfs(
    #     main_folder_path, video_name, csv_file=csv_file
    # )
    
    bbox_df = pd.read_csv(bbox_csv) if bbox_csv else None
    sequence_df = pd.read_csv(sequence_csv) if sequence_csv else None

    # Visualize the video with bounding boxes and labels
    video_name = os.path.basename(video_path)
    print(f"Video name: {video_name}")
    visualize_video_bbox._visualize_video(video_path, bbox_df, sequence_df, video_name)


if __name__ == "__main__":

    # Add args
    import argparse

    parser = argparse.ArgumentParser(
        description="Visualize video with bounding boxes and labels."
    )
    parser.add_argument(
        "--video_name",
        type=str,
        help="Name of  the video clip and camera name.",
        required=True,
    )
    parser.add_argument(
        "--bbox_csv",
        type=str,
        help="Path to the CSV file containing bounding box data.",
    )
    parser.add_argument(
        "--sequence_csv",
        type=str,
        help="Path to the CSV file containing sequence data.",
    )
    args = parser.parse_args()

    # Example usage:
    """ 
    python main.py
        --video_name "path/to/video.mp4"
        --bbox_csv "path/to/bbox.csv"
        --sequence_csv "path/to/sequence.csv"
    """

    main(args.video_name, args.bbox_csv, args.sequence_csv)
