# navigation-gesture

## Undergrads Guide
1. Annotation list: https://docs.google.com/spreadsheets/d/1-A-I4g3u3lEO5P0YNTHxZ3N3Yy2MMYA-xnFlwIAi13k/edit?usp=sharing

2. Datasets
    - CAGE: https://ucmerced.box.com/s/sfg0jnwxbcan409sfswjohdbzju9c64j
    - ITGI: https://ucmerced.box.com/s/e4n2pgg8mcdnibprfhc19gpzotgkp69m

3. Clean up bounding boxes `bbox.csv` from `raw` to `clean`. Use `visualize_bbox.py`
4. Annotate sequence. One CSV file per video. Use `visualize_bbox.py`

```
project/
├── videos/
├── info.csv
├── raw/
│   ├── bbox/
│   │   └── `video_name, camera, frame_id, pedestrian_id, x1, y1, x2, y2`
│   └── sequence/
│       └── `video_name, camera, pedestrian_id, start_frame, end_frame, gesture_label_id, ego_driver_mask`
└── clean/
    ├── bbox/
    └── sequence/
```

## Edit videos
- `concat_videos` concatenates videos
    1. With given 'search word' *(eg. "front")*
    2. Automatic finds all 'search words'
    3. Specific videos
- `cut_video` cuts videos to new files

## Annotation
1. Extract pedestrian bboxes with `scripts/extract_person_video.py`.
2. Clean up additional bboxes and ensure ID's match with `visualize_bbox.py`.
3. Construct gesture caption annotation for each pedestrian ID
    - `video_name, start_frame, end_frame, pedestrian_id, gesture_class, body_caption, gesture_caption`.
    - The gesture classes are found in `config/gesture_classes`.
    - Note: DO NOT use find-replace (replaces frames too)
4. *Optional, `scripts/stretch_annotations.py` stretches frame-stamps to each frame, including bboxes.*

## Relocate frame
`retrieve_frame` look ups the first and last frame, to relocate the original frame cut. It matches the each frame.