import os, sys
sys.path.append(".")
from scripts.concat_videos_cluster import get_camera_types

def list_equal_camera_videos(input_dir:str, video_list: str) -> list:
    """ Make lists of videos with the same camera angle. """
    
    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Input folder '{input_dir}' not found.")
    if not os.path.isdir(input_dir):
        raise NotADirectoryError(f"'{input_dir}' is not a folder.")
    
    # Get the types of video files in the folder
    camera_types = get_camera_types(input_dir)
    
    # Get list of all videos matching the video_list
    all_videos = []
    for camera_type in camera_types:
        camera_type_collection = []
        for video in video_list:
            video_path = os.path.join(input_dir, video)
            video_path = video_path.replace(".mp4", f"-{camera_type}.mp4")
            if not os.path.exists(video_path): continue
            if not os.path.isfile(video_path): continue
            if not video_path.endswith(('.mp4', '.avi', '.mov', '.MP4')): continue
            camera_type_collection.append(video_path)
        if len(camera_type_collection) == 0: continue
        all_videos.append(camera_type_collection)
    
    # Check if any video files were found
    if len(all_videos) == 0:
        raise FileNotFoundError("No video files found in the folder.")
    
    # Ensure each video collection has the same camera value
    for camera_type_collection in all_videos:
        videos = [
            video.split("-")[-1]
            for video in camera_type_collection
        ]
        if len(set(videos)) != 1:
            raise ValueError("Video collections do not match.")
        if len(videos) != len(video_list):
            raise ValueError(f"Video collection does not match.\n{camera_type_collection}")
    
    return all_videos

if __name__ == "__main__":
    
    all_videos = list_equal_camera_videos(
        input_dir = "E:/realworldgestures_original/2025-03-15_12-16-02",
        video_list = [
            "2025-03-15_12-10-56.mp4",
            "2025-03-15_12-11-57.mp4"
        ],
    )