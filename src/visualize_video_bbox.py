# %%
import cv2
import pandas as pd
import os
import sys

sys.path.append(".")
from config.gesture_classes import Gesture


def split_clip_name(video_name: str) -> tuple:
    """Split the video name into clip and camera names."""

    # Split the video name by "/"
    clip_split = video_name.split("/")
    
    # Get the clip name and camera name
    clip_name   = clip_split[0] if len(clip_split) > 0 else None
    camera_name = clip_split[1] if len(clip_split) > 1 else None

    return clip_name, camera_name


def get_video_path(
    main_folder_path: str, video_name: str, videos_folder_name: str = "videos"
) -> None:
    """Make video path and check if the video folder and CSV file exist."""

    # Check if the video folder and CSV file exist
    if not os.path.exists(main_folder_path):
        raise FileNotFoundError(f"Video folder {main_folder_path} does not exist.")
    if not os.path.isdir(main_folder_path):
        raise NotADirectoryError(f"Video folder {main_folder_path} is not a directory.")

    # Construct the video path from the main folder path and video name
    clip_split = video_name.split("/")
    video_path = (
        os.path.join(
            *[
                p
                for p in [main_folder_path, videos_folder_name] + clip_split
                if p is not None
            ]
        )
        + ".mp4"
    )
    video_path = os.path.normpath(video_path)

    # Ensure the video is valid
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video folder {video_path} does not exist.")
    if not os.path.isfile(video_path):
        raise FileNotFoundError(f"Video file {video_path} does not exist.")
    if not video_path.endswith((".mp4", ".avi", ".mov", ".MP4")):
        raise ValueError(
            f"Unsupported video format: {video_path}. Supported formats are .mp4, .avi, .mov."
        )

    return video_path


def look_for_csv_path(
    main_folder_path: str,
    video_name: str,
    csv_type: str,
    labels_folder_name: str = "labels",
) -> str:
    """Look for the CSV file in the labels folder.

    Args:
        main_folder_path (str):     Path to the main folder containing the videos and CSV files.
        video_name (str):           Name of the video clip and camera name.
        csv_type (str):             Type of CSV file to look for ('bbox' or 'sequence').
        labels_folder_name (str):   Name of the labels folder.

    Returns:
        str: Path to the CSV file.
    """

    split_clip = video_name.split("/")

    # Look for the CSV file in the 'labels' sub folders
    for version in [None, "clean", "raw"]:

        # Construct the CSV file
        csv_file = "_".join([p for p in split_clip if p is not None]) + ".csv"

        # Construct the CSV path
        csv_path = os.path.join(
            *[
                p
                for p in [
                    main_folder_path,
                    labels_folder_name,
                    version,
                    csv_type,
                    csv_file,
                ]
                if p is not None
            ]
        )
        if os.path.exists(csv_path):
            return csv_path

    # Last resort: Look for concatenated CSV file
    csv_path = look_for_concatenated_csv_path(main_folder_path, labels_folder_name)
    if csv_path is not None:
        return csv_path

    return None


def look_for_concatenated_csv_path(
    main_folder_path: str, labels_folder_name: str = "labels"
) -> str:
    """Look for the concatenated CSV file in the labels folder."""

    base_main_folder_path = os.path.basename(main_folder_path)
    csv_file = f"{base_main_folder_path}" + ".csv"
    csv_path = os.path.join(
        *[p for p in [main_folder_path, labels_folder_name, csv_file] if p is not None]
    )
    if not os.path.exists(csv_path):
        return None

    return csv_path


def load_filter_df(
    csv_path: str, video_name: list, csv_keys: list = ["video_name", "camera"]
) -> pd.DataFrame:
    """Filter the DataFrame for the given video name and camera name.

    Args:
        csv_path (str):     Path to the CSV file.
        video_name (str):   Name of the video.
        camera_name (str):  Name of the camera.
        csv_keys (list):    List of keys to filter by.

    Returns:
        pd.DataFrame: Filtered DataFrame.
    """

    if csv_path is None or not os.path.exists(csv_path):
        return None

    df = pd.read_csv(csv_path, index_col=False)

    split_clip = video_name.split("/")

    # Filter the DataFrame in hierarchical order
    for col, key in reversed(list(zip(csv_keys, split_clip))):

        # Continue if the column is not in the DataFrame or key is None
        if col not in df.columns:
            continue
        if key is None:
            continue

        # Filter first found column
        df = df[df[col] == key.lower()]
        break

    return df


def get_dfs(main_folder_path: str, video_name: str, csv_file: str = None) -> tuple:
    """Get the DataFrames for the given video name and camera name."""

    # Get the updated CSV file path
    if csv_file is None:
        bbox_csv = look_for_csv_path(main_folder_path, video_name, "bbox")
        sequence_csv = look_for_csv_path(main_folder_path, video_name, "sequence")

    # Filter the DataFrame for the given video name and camera name
    bbox_df = load_filter_df(bbox_csv, video_name)
    sequence_df = load_filter_df(sequence_csv, video_name)

    if (bbox_df is None or bbox_df.empty) and (
        sequence_df is None or sequence_df.empty
    ):
        raise ValueError(
            f"Error: No CSV files found for the video '{video_name}'. Please check the input folder."
        )

    # Ensure bbox_df contains the required columns
    required_columns = [
        "video_name",
        "camera",
        "frame_id",
        "pedestrian_id",
        "x1",
        "y1",
        "x2",
        "y2",
    ]
    for col in required_columns:
        if col not in bbox_df.columns:
            raise ValueError(
                f"Error: Missing required column '{col}' in the bounding box DataFrame. (Ensure the correct file)."
            )

    # Ensure sequence_df contains the required columns
    required_columns = [
        "video_name",
        "camera",
        "pedestrian_id",
        "start_frame",
        "end_frame",
        # "ego_driver_mask",
        "gesture_label_id",
        "body_desc",
        "interpret_desc",
    ]
    for col in required_columns:
        if col not in sequence_df.columns:
            raise ValueError(
                f"Error: Missing required column '{col}' in the sequence DataFrame. (Ensure the correct file)."
            )

    return bbox_df, sequence_df


def get_df_pedestrian(
    df_video: pd.DataFrame, frame_id: int, pedestrian_id: int
) -> pd.DataFrame:
    """Get the pedestrian ID from the DataFrame."""

    # Filter the DataFrame for the current pedestrian ID
    df_pedestrian = df_video[
        (df_video["pedestrian_id"] == pedestrian_id)
        & (df_video["frame_id"] == frame_id)
    ]
    if df_pedestrian.empty:
        return None

    return df_pedestrian


def get_bbox_from_id(df_pedestrian: pd.DataFrame, frame: int) -> tuple:
    """Get the bounding box coordinates for a given pedestrian ID from normalized coordinates to pixel values."""

    # Get the width and height of the frame
    width, height = frame.shape[1], frame.shape[0]

    # Get the bounding box coordinates
    x1_norm, y1_norm, x2_norm, y2_norm = df_pedestrian.iloc[0][
        ["x1", "y1", "x2", "y2"]
    ].values
    x1, y1, x2, y2 = (
        x1_norm * width,
        y1_norm * height,
        x2_norm * width,
        y2_norm * height,
    )
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

    return x1, y1, x2, y2


def draw_bbox(frame, x1, y1, x2, y2, pedestrian_id):
    """Draw the bounding box ID on the frame."""

    # Set the color and font for the bounding boxes
    FONT = cv2.FONT_HERSHEY_DUPLEX
    SIZE = 0.5
    WIDTH = 1
    color = (0, 255, 0)  # Standard color

    # Draw the bounding box on the frame
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, WIDTH)
    string = f"ID: {str(pedestrian_id)}"
    location = (x1, y1 - 10)
    cv2.putText(frame, string, location, FONT, SIZE, color, WIDTH)

    return frame


def get_pedestrian_label_sequence(frame_sequence, pedestrian_id):
    """Get the pedestrian label sequence from the DataFrame."""

    # Filter the DataFrame for the current pedestrian ID
    if frame_sequence is None or frame_sequence.empty:
        return None

    # Filter for the current pedestrian and frame
    frame_sequence = frame_sequence[frame_sequence["pedestrian_id"] == pedestrian_id]
    if frame_sequence.empty:
        return None

    # Get the first relevant label row
    pedestrian_sequence = frame_sequence.iloc[0] if not frame_sequence.empty else None
    
    return pedestrian_sequence


def draw_gesture_labels(frame, x1, y1, pedestrian_sequence):
    """Draw gesture labels on the frame from the DataFrame."""

    # Set the color and font for the labels
    FONT = cv2.FONT_HERSHEY_DUPLEX
    SIZE = 0.5
    WIDTH = 1

    # Check if the pedestrian sequence is None
    if pedestrian_sequence is None or pedestrian_sequence.empty:
        return frame

    # Labels we're interested in (only keep ones present)
    LABEL_KEYS = {
        "gesture_label_id": "Gesture",
        # "ego_driver_mask": "Ego Driver"
    }
    label_values = {
        value: pedestrian_sequence[key]
        for key, value in LABEL_KEYS.items()
        if key in pedestrian_sequence
    }

    # Draw available labels
    for idx, (label_name, label_value) in enumerate(label_values.items()):
        if pd.isna(label_value):  # skip NaN values
            continue
        
        # Generic label text and color
        label_text = f"{label_name}: {label_value}"
        color = (0, 0, 255) if label_value == 0 else (0, 0, 255)

        # Specific label handling
        if label_name == "Gesture":
            label_text += f" ({Gesture(label_value).name})"
            color = (
                Gesture(label_values["Gesture"]).color.value
                if "Gesture" in label_values
                else (0, 0, 255)
            )

        # Set the position for the label text
        label_position = (x1, y1 - 10 - (idx + 1) * 25)
        cv2.putText(frame, label_text, label_position, FONT, SIZE, color, WIDTH)

    return frame


def draw_bbox_duplicate_alert(frame, pedestrian_ids):
    """Draw an alert for duplicate pedestrian IDs on the frame."""

    # Set the color for the alert text
    RED_COLOR = (0, 0, 255)

    # Check for duplicate pedestrian IDs
    if not pedestrian_ids.duplicated().any():
        return frame

    # Locate center of the frame for alert text
    width, height = frame.shape[1], frame.shape[0]
    location = (width // 2 - 200, height // 2)
    cv2.putText(
        frame,
        f"Duplicate IDs detected\n{pedestrian_ids}",
        location,
        cv2.FONT_HERSHEY_DUPLEX,
        1,
        RED_COLOR,
        2,
        cv2.LINE_AA,
    )


def draw_pedestrians(frame, df_bbox, frame_id, df_sequence):
    """Draw pedestrians and their bounding boxes on the frame."""

    # Get the current frame
    current_frame = df_bbox[df_bbox["frame_id"] == frame_id]
    if current_frame.empty:
        return frame
    
    # Get the pedestrian IDs
    pedestrian_ids = current_frame["pedestrian_id"]
    if pedestrian_ids.empty:
        return frame
    
    frame_sequence = df_sequence[
        (df_sequence["start_frame"] <= frame_id) &
        (df_sequence["end_frame"] >= frame_id)
    ] if df_sequence and not df_sequence.empty else pd.DataFrame()

    for i, pedestrian_id in enumerate(pedestrian_ids):

        # Get the pedestrian DataFrame for the current ID
        pedestrian = get_df_pedestrian(df_bbox, frame_id, pedestrian_id)
        if pedestrian is None:
            continue

        # Draw alert for duplicate IDs
        draw_bbox_duplicate_alert(frame, pedestrian_ids)

        # Get the bounding box coordinates
        x1, y1, x2, y2 = get_bbox_from_id(pedestrian, frame)
        draw_bbox(frame, x1, y1, x2, y2, pedestrian_id)

        # Get and draw gesture labels
        pedestrian_sequence = get_pedestrian_label_sequence(
            frame_sequence, pedestrian_id
        )
        draw_gesture_labels(frame, x1, y1, pedestrian_sequence)

    return frame


def draw_info(frame, video_name, frame_id, interval):
    """Draw the video name, frame number, and interval on the frame."""

    info = [
        f"Video: {video_name}",
        f"Frame: {frame_id}",
        f"Speed: {int(64/interval)}",
    ]
    for i, text in enumerate(info):
        cv2.putText(
            frame,
            text,
            (20, 50 + i * 50),
            cv2.FONT_HERSHEY_DUPLEX,
            1,
            (0, 0, 0),
            1,
            cv2.LINE_AA,
        )

    return frame


class Controller:
    def __init__(self, total_frames):
        # Set default values for the controller
        self.play = False
        self.frame_id = 0
        self.speed = 8
        self.max_speed = 64
        self.show_hud = True

        # Set the total number of frames
        self.total_frames = total_frames

    def control_video_playback(self):
        """Control video playback with keyboard input."""

        # Get key press
        key = cv2.waitKeyEx(self.speed if self.play else 0)
        # print(f"Key pressed: {key}")

        # Control HUD visibility
        self.show_hud = (
            not self.show_hud if key == 104 else self.show_hud
        )  # 'h' to toggle HUD

        # Control playback state
        self.play = (
            not self.play if key == 32 else self.play
        )  # Space to toggle play/pause
        exit() if key == 113 else None  # 'q' to exit

        self._interval_control(key)
        self._update_frame_id(key)

    def _interval_control(self, key):
        """Control the interval for frame navigation."""
        # Control playback speed and frame navigation
        self.speed /= 2 if key in (2490368, ord('w')) else 1  # Up arrow or 'w' key
        self.speed *= 2 if key in (2621440, ord('s')) else 1  # Down arrow or 's' key
        self.speed = min(self.speed, self.max_speed)  # Limit max speed
        self.speed = max(self.speed, 1)  # Limit min speed to 1
        self.speed = int(self.speed)  # Convert to int for cv2.waitKeyEx

    def _update_frame_id(self, key):
        """Update the frame ID based on key presses."""

        self.frame_id += 1 if self.play else 0  # Play mode

        # Control frame navigation
        interval = self.max_speed / self.speed
        self.frame_id -= interval if key in (2424832, ord('a')) else 0  # Left arrow or 'a' key
        self.frame_id += interval if key in (2555904, ord('d')) else 0  # Right arrow or 'd' key

        # Keep frame_id within bounds by wrapping around
        self.frame_id = 0 if self.frame_id >= self.total_frames else self.frame_id
        self.frame_id = self.total_frames - 1 if self.frame_id < 0 else self.frame_id

        return


def visualize_video(
    video_path: str,
    df_bbox: pd.DataFrame,
    df_sequence: pd.DataFrame,
    video_name: str = None,
) -> None:
    """Visualize the video with bounding boxes and labels.

    Args:
        video_path (str): Path to the video file.
        df_bbox (pd.DataFrame): DataFrame containing bounding box information.
        df_sequence (pd.DataFrame): DataFrame containing sequence information.
    """

    # Load the video
    cap = cv2.VideoCapture(video_path)
    # Get variables from the video
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    # Initialize the controller
    controller = Controller(total_frames)

    # Create a window to display the video
    while cap.isOpened():

        # Check if the video is playing or paused and read the frame
        if not controller.play:
            cap.set(cv2.CAP_PROP_POS_FRAMES, controller.frame_id - 1)

        ret, frame = cap.read()
        if not ret:
            break
        controller.frame_id = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

        # Draw bounding boxes on the frame
        if controller.show_hud:
            frame = draw_pedestrians(frame, df_bbox, controller.frame_id, df_sequence)
            frame = draw_info(frame, video_name, controller.frame_id, controller.speed)

        # Display the frame
        frame = cv2.resize(frame, (1280, 720))
        cv2.imshow("Processed Video", frame)
        controller.control_video_playback()

    # Release the VideoCapture and VideoWriter objects
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    pass
