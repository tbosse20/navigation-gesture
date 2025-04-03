import cv2
import os
from tqdm import tqdm
from ultralytics import YOLO
import torch
import cv2
import logging
import numpy as np

# Suppress YOLOv8 logging
logging.getLogger("ultralytics").setLevel(logging.ERROR)

def update_csv_path(videos_folder_path: str, output_folder: str, concat: bool = False) -> str:
    """ Updates the CSV path based on the video folder and output folder.
    
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
    
    # Ensure output folder exists
    os.makedirs(output_folder, exist_ok=True)
        
    # Make initial CSV path
    csv_filename = f"{videos_folder_name}_unclean_bbox.csv"
    csv_path = os.path.join(output_folder, csv_filename)
    
    # Skip if individual CSV files are not needed and the file already exists
    if not concat or os.path.exists(csv_path):
        return csv_path
    
    # Make concatenated CSV file
    with open(csv_path, 'w') as f:
        f.write("video_name,frame_id,pedestrian_id,x1,y1,x2,y2\n")
            
    return csv_path

def extract_person_from_videos(videos_folder_path: str, output_folder: str, concat: bool = True):
    """ Extracts people from video folder and saves them with bounding boxes and tracking IDs in a CSV file.
    
    Args:
        videos_folder (str): Path to the folder containing video files.
    """
    
    # Check if the video folder exists and is a directory
    if not os.path.exists(videos_folder_path):
        raise FileNotFoundError(f"Main folder {videos_folder_path} does not exist.")
    if not os.path.isdir(videos_folder_path):
        raise NotADirectoryError(f"Main folder {videos_folder_path} is not a directory.")
    
    # Get videos from the main folder
    video_files = [
        video_file
        for video_file in os.listdir(videos_folder_path)
        if video_file.endswith(('.mp4', '.avi', '.mov', '.MP4'))
    ]
    
    # Check if any video files were found
    if len(video_files) == 0:
        print("Error: No video files found in the folder.")
        return
    
    # Update CSV path
    concat_csv_path = update_csv_path(videos_folder_path, output_folder, concat=concat)
    
    # Process each video file
    for video_file in tqdm(video_files, desc="Videos"):
        
        # Convert to individual CSV file
        video_name = video_file.split(".")[0]
        individual_csv_path = concat_csv_path.replace('.csv', f'_{video_name}.csv')
        current_csv_path = concat_csv_path if concat else individual_csv_path
        
        # Run pose extraction
        video_path = os.path.join(videos_folder_path, video_file)
        pose_from_video(video_path, current_csv_path, concat=concat)

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
    """ Extracts people from video and saves them with bounding boxes and tracking IDs in a CSV file. """
    
    # Check if the video file exists and is a valid format
    if not os.path.exists(video_path):
        print(f"Error: Video file {video_path} does not exist.")
        return
    if not os.path.isfile(video_path):
        print(f"Error: Video file {video_path} is not a file.")
        return
    if not video_path.endswith(('.mp4', '.avi', '.mov', '.MP4')):
        print(f"Error: Video file {video_path} is not a valid video format.")
        return
    
    # Create individual CSV file for each video if it doesn't exist
    if not os.path.exists(csv_path) and not concat:
        with open(csv_path, 'w') as f:
            f.write("video_name,frame_id,pedestrian_id,x1,y1,x2,y2\n")
    else:
        return # Skip if the file already exists and concatenation is not needed
    
    # Get existing lines from the CSV file to test for duplicates
    with open(csv_path, 'r') as f:
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
        video_name = os.path.basename(result.path)
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
            x1_norm, y1_norm, x2_norm, y2_norm = np.array([x1, y1, x2, y2]) / np.array([width, height, width, height])
            pedestrian_id = int(box.id[0]) if box.id is not None else -1
            
            # Append result to CSV
            with open(csv_path, 'a') as f:
                f.write(f"{video_name},{frame_id},{pedestrian_id},{x1_norm},{y1_norm},{x2_norm},{y2_norm}\n")
                
if __name__ == "__main__":
    
    # Add args
    import argparse
    parser = argparse.ArgumentParser(description="Extract people from videos and save to CSV.")
    parser.add_argument("--videos_folder",  type=str,           help="Path to the folder containing video files.",  required=True)
    parser.add_argument("--output_folder",  type=str,           help="Path to the output folder for CSV files.",    default="data/labels/")
    parser.add_argument("--concat",     action="store_true",    help="Concatenate CSV files.",  dest="concat")
    parser.add_argument("--indi", action="store_false",   help="Invidivual CSV files.",   dest="concat")
    parser.set_defaults(concat=True)
    args = parser.parse_args()
    
    extract_person_from_videos(args.videos_folder, args.output_folder, args.concat)