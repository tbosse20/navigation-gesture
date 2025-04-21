# CANG-data annotation
## Annotation Conflicting Authorities & Navigation Gestures (CANG)

## Datasets
- CANG: https://ucmerced.box.com/s/sfg0jnwxbcan409sfswjohdbzju9c64j
- ITGI: https://ucmerced.box.com/s/e4n2pgg8mcdnibprfhc19gpzotgkp69m

## Assigning
- Annotation task list: https://docs.google.com/spreadsheets/d/1-A-I4g3u3lEO5P0YNTHxZ3N3Yy2MMYA-xnFlwIAi13k/edit?usp=sharing
- Deadline: 4th May 2025 11:59 PM

## Annotation Guide

<!-- 1. Edit videos
    1. `concat_videos` concatenates videos
        1. With given 'search word' *(eg. "front")*
        1. Automatic finds all 'search words'
        1. Specific videos
    1. `cut_video` cuts videos to new files -->

<!-- 1. Extract pedestrian bboxes with `scripts/extract_person_video.py`. -->

- Use `main.py` to visualize the video and bounding box with frames.
    - Input:
        - `--main_folder_path` (str): Path to the main folder containing the videos and CSV files.
            - *(e.g. `../conflict_acted_navigation_gestures`)*
        - `--video_name` (str): Name of the video clip and camera name.
            - *(e.g. `video_02/front`)*
    - Controls:
        - Space:        Play/Pause
        - Up Arrow:     Increase playback
        - Down Arrow:   Decrease playback
        - Left Arrow:   Backward 10 frames
        - Right Arrow:  Forward 10 frames
        - 'h':          Toggle HUD
        - 'q':          Quit

- See `video_13_front' for example.

- *Upload to this link, if editing of the Box isn't permitted: https://drive.google.com/drive/folders/1wCjvZFx-nsZkZc4NegPH5MZOhGuWQBdp?usp=sharing*

1. Clean up `bbox.csv`, by remove additional bounding boxes and match ID's. Move from `raw` to `clean` when done.
    - Note: Be aware when using '*find-replace*'-function (replaces frames too)!

1. Annotate sequences for each pedestrian ID. One CSV file per video.
    - `video_name, camera, pedestrian_id, start_frame, end_frame, gesture_class, body_desc, gesture_desc`.
    <!-- ego_driver_mask,  -->
    - The `gesture_class` is found in `config/gesture_classes`.
    - See detailed description in PDF file, *4.2. Annotation Framework*.
    
<!-- 1. *Optional, `scripts/stretch_annotations.py` stretches frame-stamps to each frame, including bboxes.* -->

## Dataset Structure
```
project/
├── info.csv
├── videos/
│   ├── video_00.mp4
│   ├── video_01.mp4
│   └── ...
├── raw/
│   ├── bbox/
│   │   ├── video_00_front.csv
│   │   ├── video_01_front.csv
│   │   └── ...
│   └── sequence/
│       ├── video_00_front.csv
│       ├── video_01_front.csv
│       └── ...
└── clean/
    ├── bbox/
    │   ├── video_00_front.csv
    │   └── ...
    └── sequence/
        ├── video_00_front.csv
        └── ...
```

<!-- ## Relocate frame
`retrieve_frame` look ups the first and last frame, to relocate the original frame cut. It matches the each frame. -->

<!-- ## Future Work
- Expand dataset to include none-direct gestures too. -->