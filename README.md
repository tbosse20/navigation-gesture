# CANG-data annotation
## Annotation Conflicting Authorities & Navigation Gestures (CANG)

## Datasets
- CANG: https://ucmerced.box.com/s/sfg0jnwxbcan409sfswjohdbzju9c64j
- ITGI: https://ucmerced.box.com/s/e4n2pgg8mcdnibprfhc19gpzotgkp69m

## Annotation Guide
1. Download your assigned files from the Box. The structure doesn't matter. You'll have to specify the locations anyways.

1. Download libraries `pip install -r requirements.txt`.

1. Edit videos
    1. `concat_videos` concatenates videos
        1. With given 'search word' *(eg. "front")*
        1. Automatic finds all 'search words'
        1. Specific videos
    1. `cut_video` cuts videos to new files

1. Extract pedestrian bboxes with `scripts/extract_person_video.py`.

- Use `main.py` to visualize the video and bounding box with frames.
    - Input:
        - `--video_path` (str): Path to the video file.
        - `--bbox_csv` (str): Path to the bbox csv file.
        - `--sequence_csv`(str): Path to the sequence csv file. (*Count 'commas' if it doesn't appear*)
        
    - Controls:
        - Space:                           Play/Pause
        - Up/down Arrow or 'w'/'s' key:    Increase/Decrease playback speed
        - Left/right Arrow or 'a'/'d' key: Backward/forward X frames (depends on speed)
        - 'h' key:                         Toggle HUD
        - 'q' key:                         Quit

- See ITGI `video_13_front' for example.

- *Upload to this link, if editing of the Box isn't permitted: https://drive.google.com/drive/folders/1wCjvZFx-nsZkZc4NegPH5MZOhGuWQBdp?usp=sharing*

1. Clean up `bbox.csv`, by remove additional bounding boxes and match ID's. Move from `raw` to `clean` when done.
    - Note: Be aware when using '*find-replace*'-function (replaces frames too)!

1. Make your own `sequence.csv` file. Annotate sequences for each pedestrian ID, but only gesture directed to the ego driver! One CSV file per video.
    - `video_name, camera, pedestrian_id, start_frame, end_frame, gesture_class, body_desc, gesture_desc`.
    <!-- ego_driver_mask,  -->
    - The `gesture_class` is found in `config/gesture_classes`.
    - See detailed description in PDF file, *4.2. Annotation Framework*.
    - Authority IDs: 0. Officer, 1. Firefighter, 2. Civilian, 3. Safety vest, 4. Unlisted, 5. Unclear
    
1. *Optional, `scripts/stretch_annotations.py` stretches frame-stamps to each frame, including bboxes.*

## Online Dataset Structure
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

## Relocate frame
`retrieve_frame` look ups the first and last frame, to relocate the original frame cut. It matches the each frame.

## Future Work
- Expand dataset to include none-direct gestures too.