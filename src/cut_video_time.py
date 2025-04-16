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
    
    # Run ffmpeg command
    command = [
        "ffmpeg",
        "-ss",
        str(start_time),  # Accurate when placed before -i with re-encode
        "-i",
        input_file,
        "-t",
        str(duration),
        "-an",  # Remove audio
        "-c:v",
        "libx264",  # Re-encode video
        "-preset",
        "fast",  # Speed vs compression tradeoff
        output_file,
    ]
    subprocess.run(command, check=True)