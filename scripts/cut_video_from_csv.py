import os
import pandas as pd
import sys
sys.path.append(".")
import scripts.video_edit as video_edit

def cut_video_cluster( video_path: str, start_frame_index: int, end_frame_index: int, output_file_path: str):
    """ Cut the videos in the given path using the provided start and end frame indices. """

    # Get the output file name and path
    output_file_dir = output_file_path.split(".mp4")[0]
    os.makedirs(output_file_dir, exist_ok=True)
    
    # Get videos in file
    video_files = [
        os.path.join(video_path, f)
        for f in os.listdir(video_path)
        if f.endswith((".mp4", ".avi", ".mov", ".MP4"))
    ]
    
    for video_file in video_files:
        
        # Check if the video file exists
        if not os.path.exists(video_file):
            print(f"Video file {video_file} does not exist. Skipping.")
            continue
        
        video_name = os.path.basename(video_file)
        output_file_path = os.path.join(output_file_dir, video_name)

        if os.path.exists(output_file_path):
            print(f"'{output_file_path}' already exists.")
            continue
        else:
            print(f"Cutting {output_file_path}.")
        
        # Cut the video using the provided start and end times
        video_edit.cut_video_frames(
            input_file  = video_file,
            start_frame = start_frame_index,
            end_frame   = end_frame_index,
            output_name = output_file_path,
        )
                
def cut_with_csv(csv_file: str, output_extension: str = "cut"):
    """ Cut the videos in the CSV file, using the given information.
    
    Args: 
        csv_file (str): Path to the CSV file containing video information.
    
    Returns:
        None: The function saves the cut videos in the specified output folder "cut".
    """
    
    # Load the CSV file
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"CSV file {csv_file} does not exist.")
    if not os.path.isfile(csv_file):
        raise NotADirectoryError(f"CSV file {csv_file} is not a file.")
    
    # Read the CSV file
    df = pd.read_csv(csv_file)
    
    # Check if the required columns are present
    required_columns = ["video_path", "start_frame_index", "end_frame_index"]
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"Missing required column '{col}' in CSV file.")
    
    # Iterate through each row in the DataFrame
    for index, row in df.iterrows():
        video_path        = row["video_path"]
        start_frame_index = row["start_frame_index"]
        end_frame_index   = row["end_frame_index"]
        
        # Create the output folder for cut videos
        output_folder = f"{os.path.dirname(video_path)}_{output_extension}"
        os.makedirs(output_folder, exist_ok=True)
        
        # Check if the video file exists
        if not os.path.exists(video_path):
            print(f"Video file {video_path} does not exist. Skipping.")
            continue
        
        # Get the output file name and path
        output_file_name = f"video_{index:02d}.mp4"
        output_file_path = os.path.join(output_folder, output_file_name)
        
        if os.path.isfile(video_path):
            # Cut the video using the provided start and end times
            video_edit.cut_video_frames(
                input_file  = video_path,
                start_frame = start_frame_index,
                end_frame   = end_frame_index,
                output_name = output_file_path,
            )
        
        elif os.path.isdir(video_path):
            cut_video_cluster(
                video_path        = video_path,
                start_frame_index = start_frame_index,
                end_frame_index   = end_frame_index,
                output_file_path  = output_file_path,
            )

if __name__ == "__main__":
    
    import argparse
    parser = argparse.ArgumentParser(description="Cut videos using information from a CSV file.")
    parser.add_argument("--csv_file", type=str, help="Path to the CSV file containing video information.")
    args = parser.parse_args()
    
    cut_with_csv(args.csv_file)