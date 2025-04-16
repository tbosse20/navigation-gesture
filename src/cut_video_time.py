import subprocess

def cut_video_time(input_file: str, output_file: str, start_time: int, duration: int) -> None:
    """Cut a video file using ffmpeg with start time and duration.
    
    Args:
        input_file  (str): Path to the input video file.
        output_file (str): Path to the output video file.
        start_time  (int): Start time in seconds.
        duration    (int): Duration in seconds.
        
    Returns:
        None: A new video file is created in the specified output path.
    """