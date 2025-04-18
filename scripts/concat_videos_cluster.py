import os
import subprocess
from tqdm import tqdm


def write_txt_file(video_paths: list, LIST_FILE="file_list.txt") -> None:
    """Write video paths to a file list for ffmpeg."""

    # Delete the file if it already exists
    if os.path.exists(LIST_FILE):
        os.remove(LIST_FILE)

    # Write video paths to the file list
    with open(LIST_FILE, "w") as f:
        for video_path in video_paths:
            f.write(f"file '{video_path}'\n")

    return LIST_FILE


def get_camera_types(input_dir: str) -> list:
    """Get the types of camera angles in the dir."""

    if not os.path.exists(input_dir):
        raise FileNotFoundError(f"Input dir '{input_dir}' not found.")
    if not os.path.isdir(input_dir):
        raise NotADirectoryError(f"'{input_dir}' is not a dir.")

    # Get the types of video files in the dir
    camera_types = []
    for _, _, files in os.walk(input_dir):
        for video in files:
            if not video.endswith((".mp4", ".avi", ".mov", ".MP4")):
                continue
            camera_type = video.split("-")[-1].split(".")[0]
            camera_types.append(camera_type)

    # Remove duplicates
    camera_types = list(set(camera_types))

    return camera_types


def concat_dir_videos(
    parent_dir: str, manual_include_word: str = None, extension_name: str = "concat"
) -> None:
    """Concatenate videos from the same dir, with the given 'search word'.

    Args:
        parent_dir (str):     The parent dir containing sub dirs with videos.
        include_word  (str):  Only include video files containing this word.
        extension_name (str): The name of the output dir.

    Input Structure:
        parent_dir/
        ├── subdir1/
        │   ├── video1-left.mp4
        │   ├── video1-right.mp4
        │   ├── video2-left.mp4
        │   ├── video2-right.mp4
        ├── subdir2/
        │   ├── video1-left.mp4
        │   ├── video1-right.mp4
        │   ├── video2-left.mp4
        │   ├── video2-right.mp4
        ...

    Output *(manual_include_word = None)*:
        parent_dir_concat/
        ├── subdir1/
        │   ├── video-left.mp4
        │   ├── video-right.mp4
        ├── subdir2/
        │   ├── video-left.mp4
        │   ├── video-right.mp4
        ...

    Output *(manual_include_word = "left")*:
        parent_dir_concat/
        ├── subdir1(-left).mp4
        ├── subdir2(-left).mp4
        ...
    """

    # Check if the parent dir exists and is a dir
    if not os.path.exists(parent_dir):
        raise FileNotFoundError(f"Directory '{parent_dir}' not found.")
    if not os.path.isdir(parent_dir):
        raise NotADirectoryError(f"'{parent_dir}' is not a directory.")

    # Create output dir as sibling of parent dir
    output_dir = os.path.join(f"{parent_dir}_{extension_name}", "videos")
    os.makedirs(output_dir, exist_ok=True)

    # Get sub dirs
    input_dirs = [f.path for f in os.scandir(parent_dir) if f.is_dir()]
    if len(input_dirs) == 0:
        raise FileNotFoundError(f"No sub dirs found in '{parent_dir}'.")

    concat_subdir(
        input_dir=input_dirs,
        output_dir=output_dir,
        manual_include_word=manual_include_word,
    )


def concat_subdir(input_dir: list, output_dir: str, manual_include_word: str) -> None:
    """Concatenate videos from the same dir. Clusters given 'manual_include_word' or found itself. 
    
    Args:
        input_dir (list):    The list of input dirs containing videos.
        output_dir (str):    The output dir to save the concatenated videos.
        manual_include_word (str): Only include video files containing this word.
        
    Returns:
        None: Saves the concatenated videos to the output dir.
    """

    # Loop through sub dirs
    for input_dir in tqdm(input_dir, desc="Processing sub dirs"):

        # Set input and output names
        input_name = os.path.basename(input_dir)
        output_name = os.path.join(output_dir, input_name)

        # Get camera types from the parent dir
        camera_types = (
            get_camera_types(input_dir)
            if manual_include_word is None
            else [manual_include_word]
        )

        # Loop through camera types
        for include_word in camera_types:

            # Create output dir if multiple camera types are found and update the output name
            if manual_include_word is None:
                os.makedirs(output_name, exist_ok=True)
                current_output_file = os.path.join(output_name, include_word)

            # Create output file name
            current_output_file = current_output_file + ".mp4"
            # Skip if the output file already exists
            if os.path.exists(current_output_file):
                print(f"'{input_name}' already exists, skipping.")
                continue

            # Concatenate videos in the sub dir
            concat_videos(
                input_dir=input_dir,
                output_file=current_output_file,
                include_word=include_word,
            )


def concat_videos(input_dir: str, output_file: str, include_word: str) -> None:
    """Concatenate videos from the same dir, with the given 'search word'.
    
    Args:
        input_dir (str):     The dir containing the videos.
        output_file (str):   The output file name.
        include_word (str):  Only include video files containing this word.
        
    Returns:
        None: Saves the concatenated video to the output file.
    """

    # Get video files containing 'search word', reverse order
    video_list = [
        os.path.join(input_dir, f.name)
        for f in os.scandir(input_dir)
        if f.is_file() and include_word in f.name
    ]
    if len(video_list) == 0:
        return
    
    # Sort according to video name ex. '2025-03-18_14-27-29-front.mp4'
    video_list.sort(key=lambda x: x.split("/")[-1].split("-")[0])
    
    # Write video paths to the file list
    list_file = write_txt_file(video_list)

    # Construct ffmpeg command
    command = [
        "ffmpeg",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        list_file,
        "-c",
        "copy",
        output_file,
    ]

    # Run ffmpeg command
    try:
        subprocess.run(
            command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Command: {' '.join(command)}")
        print(f"Output file: {output_file}")
        print(f"List file: {list_file}")
        raise e
    except Exception as e:
        print(f"Unexpected error: {e}")
        print(f"Command: {' '.join(command)}")
        print(f"Output file: {output_file}")
        print(f"List file: {list_file}")
        raise e

    # Remove the file list
    os.remove(list_file)
    

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Concatenate videos from the same dir with the same 'search word'."
    )
    parser.add_argument(
        "--input_dir",
        type=str,
        help="The parent dir containing sub dirs with videos.",
        required=True,
    )
    parser.add_argument(
        "--include_word",
        type=str,
        default=None,
        help="Only include video files containing this word.",
    )
    args = parser.parse_args()
    
    # Example usage:
    """ 
    python scripts/concat_videos_cluster.py \
        --input_dir ../data/actedgestures_original
    """

    concat_dir_videos(
        parent_dir=args.input_dir,
        manual_include_word=args.include_word,
    )
