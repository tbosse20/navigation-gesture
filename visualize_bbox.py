import os
import sys

sys.path.append(".")
import src.visualize_video_bbox as visualize_video_bbox


def main(main_folder_path: str, video_name: str, csv_file: str = None) -> None:
    """Visualize the video with bounding boxes and labels. Works only on clusters.

    Args:
        main_folder_path    (str):  Path to the main folder containing the videos and CSV files.
        video_name          (str):  Name of the video clip and camera name.

    Control:
        - Space:        Play/Pause
        - Up Arrow:     Increase interval
        - Down Arrow:   Decrease interval
        - Left Arrow:   Backward frames
        - Right Arrow:  Forward frames
        - 'h':          Toggle HUD
        - 'q':          Quit

    Raises:
        FileNotFoundError:  If the video file does not exist.
        ValueError:         If the video format is not supported.
        ValueError:         If the CSV files are empty.

    Returns:
        None: Only visualizes the video with bounding boxes and labels.
    """
    
    video_path = visualize_video_bbox.get_video_path(
        main_folder_path, video_name
    )

    # Retrieve the CSV files for the video
    df_bbox, df_video_labels = visualize_video_bbox.safe_data_retrieve(
        main_folder_path, video_name
    )

    # Visualize the video with bounding boxes and labels
    visualize_video_bbox._visualize_video(video_path, df_bbox, df_video_labels, video_name)


if __name__ == "__main__":

    # Add args
    import argparse

    parser = argparse.ArgumentParser(
        description="Visualize video with bounding boxes and labels."
    )
    parser.add_argument(
        "--main_folder",
        type=str,
        help="Path to the main folder containing the videos.",
        required=True,
    )
    parser.add_argument(
        "--video_name",
        type=str,
        help="Name of  the video clip and camera name.",
        required=True
    )
    args = parser.parse_args()

    # Example usage:
    """ 
    python visualize_bbox.py --main_folder "../data/conflict_acted_navigation_gestures" --video_name "video_00/front"
    """

    main(args.main_folder, args.video_name)
