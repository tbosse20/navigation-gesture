import os
import cv2
from skimage.metrics import structural_similarity as ssim
from tqdm import tqdm
import numpy as np
import pandas as pd

def find_frame_in_video(frame: np.ndarray, video_path: str) -> int:
    """ Find the frame in a video that matches the given frame.
    
    Args:
        frame (np.ndarray): Frame to be matched.
        video_path (str): Path to the video file.
        
    Return:
        int: Frame number of the matching frame, or -1 if not found.
    """
    
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    video_name = os.path.basename(video_path)
    
    # Loop through frames in the video
    frame_number = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    with tqdm(total=total_frames, desc=video_name) as pbar:
        while True:
            ret, current_frame = cap.read()
            if not ret: break
            
            # Compare frames
            if np.all(frame == current_frame):
                cap.release()
                return frame_number
            
            frame_number += 1
            pbar.update(1)
            
    return -1  # Frame not found

def filter_with_csv(original_videos: list, csv_helper_path: str, target_video: str) -> list:
    """ Filter original videos based on the date_time in the CSV helper file.
    (
        Note: Will not work across folders. Add manually if needed when filtering. Eg.:
        ``` if date_time in video_path or "2025-03-15_13-23-36" in video_path ```
    )
    
    Args:
        original_videos (list): List of original video paths.
        csv_helper_path (str): Path to the CSV helper file.
        target_video (str): Path to the target video file.
        
    Return:
        list: Filtered list of original video paths.
    """
    
    if csv_helper_path is None:
        raise ValueError("CSV helper path is None.")
        
    # Read the CSV helper file
    df_helper = pd.read_csv(csv_helper_path, index_col=False)
    if df_helper.empty:
        raise ValueError("CSV helper file is empty.")
    
    # Get the target video basename and date_time from the CSV helper file
    target_video_basename = os.path.basename(target_video).split(".")[0]
    df_row = df_helper[df_helper["video_name"] == target_video_basename]
    if df_row.empty:
        raise ValueError(f"Target video {target_video_basename} not found in CSV helper file.")
    date_time = df_row["date_time"].values[0]
    
    # Filter original videos based on date_time
    original_videos = [
        video_path
        for video_path in original_videos
        if (date_time in video_path
            # or "2025-03-15_13-23-36" in video_path  # Uncomment if needed
        )
    ]
    
    if len(original_videos) == 0:
        raise FileNotFoundError(f"No original videos found with date_time {date_time}.")
    
    # Sort original videos by modification time
    original_videos = sorted(original_videos, key=lambda x: os.path.getmtime(x))
    
    return original_videos

def get_lookup_videos(original_videos_dir: str) -> list:
    """ Get the original videos containing "front" in their names. 
    
    Args:
        original_videos_dir (str): Path to the directory containing original videos.
        
    Return:
        list: List of original video paths.
    """

    # Scrape videos (Add containing "front" in sub folders) 
    original_videos = [
        os.path.join(root, file)
        for root, _, files in os.walk(original_videos_dir)
        for file in files
        if (file.endswith(('.mp4', '.avi', '.mov', '.MP4'))
            # and "front" in file
        )
    ]
    if len(original_videos) == 0:
        raise FileNotFoundError(f"No original videos found in {original_videos_dir}.")
        
    return original_videos

def get_start_end_frame(target_cap: cv2.VideoCapture) -> tuple:
    """ Get the start and end frames of a video.
    
    Args:
        target_cap (str): Path to the target video file.
        
    Return:
        tuple: Start and end frames of the video.
    """
    
    # Get first frame of the target video
    _, start_frame = target_cap.read()
    
    if start_frame is None:
        raise ValueError(f"Failed to read the 'first' frame.")
    
    # Retrieve the last frame of the video
    # Set to the last frame (indexing starts at 0)
    estimated_total = int(target_cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    # Try to find the last decodable frame by going backwards
    last_frame = None
    for i in reversed(range(estimated_total)):
        target_cap.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = target_cap.read()
        if ret and frame is not None:
            last_frame = frame
            break
        
    if last_frame is None:
        raise ValueError(f"Failed to read the 'last' frame.")
    
    return start_frame, last_frame

def retrieve_frame(target_video: str, original_videos_dir: str, csv_helper_path: str) -> int:
    """ Compare the first frame with a video and retrieve the frame number.
    
    Args:
        original_videos_dir (str): Path to the directory containing original videos.
        target_video (str): Path to the target video file.
        
    Return:
        int: Frame number of the first frame that matches the target video.
    """
    
    # Check if the target video exists and is a file
    if not os.path.exists(target_video):
        raise FileNotFoundError(f"Target video {target_video} does not exist.")
    if not os.path.isfile(target_video):
        raise NotADirectoryError(f"Target video {target_video} is not a file.")
    
    # Check if the original videos directory exists and is a directory
    if not os.path.exists(original_videos_dir):
        raise FileNotFoundError(f"Original video {original_videos_dir} does not exist.")
    if not os.path.isdir(original_videos_dir):
        raise NotADirectoryError(f"Original video {original_videos_dir} is not a directory.")
    
    # Get all video files in the original videos directory
    original_videos = get_lookup_videos(original_videos_dir)
    original_videos = filter_with_csv(original_videos, csv_helper_path, target_video)
    print("Original videos found:", len(original_videos))

    # Open the target video
    target_cap = cv2.VideoCapture(target_video)
    start_frame, last_frame = get_start_end_frame(target_cap)
    target_cap.release()
    
    # Initialize data dictionary
    data = {"target_video": target_video}
    
    # Set the target frame to the first frame of the target video
    target_frame = start_frame.copy()
    
    for original_video_path in original_videos:
        
        # Get the frame number of the matching frame
        frame_number = find_frame_in_video(target_frame, original_video_path)
        if frame_number == -1: continue
            
        # Save as start frame
        if "start_frame_number" not in data:
            print("Start frame:", frame_number, original_video_path)
            data["start_video_path"] = original_video_path
            data["start_frame_number"] = frame_number
            
            # Update and check same video
            target_frame = last_frame.copy()
            frame_number = find_frame_in_video(target_frame, original_video_path)
            if frame_number == -1: continue
            
            # Save as last frame if found
            print("End frame:", frame_number, original_video_path)
            data["last_video_path"] = original_video_path
            data["last_frame_number"] = frame_number
            return data
        
        elif "last_frame_number" not in data:
            # Save as last frame if found in later videos
            print("End frame:", frame_number, original_video_path)
            data["last_video_path"] = original_video_path
            data["last_frame_number"] = frame_number
            return data
            
    return None

def retrieve_frame_folder(target_videos_dir: str, original_videos_dir:str, csv_helper: str) -> None:
    """ Retrieve frame numbers from all videos in a directory. """
    
    # Check if the target videos directory exists and is a directory
    if not os.path.exists(target_videos_dir):
        raise FileNotFoundError(f"Target videos directory {target_videos_dir} does not exist.")
    if not os.path.isdir(target_videos_dir):
        raise NotADirectoryError(f"Target videos directory {target_videos_dir} is not a directory.")
    
    # Get all video files in the target videos directory
    target_videos = [
        os.path.join(target_videos_dir, file)
        for file in os.listdir(target_videos_dir)
        if file.endswith(('.mp4', '.avi', '.mov', '.MP4'))
    ]
    if len(target_videos) == 0:
        raise FileNotFoundError(f"No target videos found in {target_videos_dir}.")
    
    # Make a csv file to print the results
    csv_file = os.path.join(target_videos_dir, "retrieved_frames.csv")
    if not os.path.exists(csv_file):
        with open(csv_file, "w") as f:
            f.write("target_video,start_video_path,start_frame_number,last_video_path,last_frame_number\n")
    
    for target_video in target_videos:
        print("Processing:", target_video)
        data = retrieve_frame(target_video, original_videos_dir, csv_helper)
        if data is None:
            continue
        
        with open(csv_file, "a") as f:
            f.write(f"{data['target_video']},{data['start_video_path']},{data['start_frame_number']},"
                    f"{data['last_video_path']},{data['last_frame_number']}\n")

if __name__ == "__main__":
    
    import argparse
    parser = argparse.ArgumentParser(description="Retrieve frame number from original video.")
    parser.add_argument("--target_video", type=str, help="Path to the target video file.")
    parser.add_argument("--target_videos_dir", type=str, help="Path to the target videos directory.")
    parser.add_argument("--original_videos_dir", type=str, help="Path to the original videos directory.", required=True)
    parser.add_argument("--csv_helper", type=str, help="Path to the CSV helper file.", default=None)
    args = parser.parse_args()
    
    """ Example usage:
    python scripts/retrieve_frame.py `
        --target_videos_dir "../realworldgestures" `
        --original_videos_dir "e:/realworldgestures_original_temp" `
        --csv_helper "../realworldgestures/Description.txt"
    """
    
    if args.target_videos_dir:
        retrieve_frame_folder(args.target_videos_dir, args.original_videos_dir, args.csv_helper)
    elif args.target_video:
        data = retrieve_frame(args.target_video, args.original_videos_dir, args.csv_helper)
        if data is not None:
            print("Matching frames found:")
            print("Target video:", data["target_video"])
            print("Start frame:", data["start_frame_number"], data["start_video_path"])
            print("End frame:", data["last_frame_number"], data["last_video_path"])
        else:
            print("No matching frame found..")
    else:
        raise ValueError("Either --target_video or --target_videos_dir must be provided.")