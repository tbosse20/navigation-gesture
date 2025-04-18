# navigation-gesture

## Guide
Undergrads
- Annotation list: https://docs.google.com/spreadsheets/d/1-A-I4g3u3lEO5P0YNTHxZ3N3Yy2MMYA-xnFlwIAi13k/edit?usp=sharing

CAGE: https://ucmerced.box.com/s/sfg0jnwxbcan409sfswjohdbzju9c64j
ITGI: https://ucmerced.box.com/s/e4n2pgg8mcdnibprfhc19gpzotgkp69m

## Edit videos
- `video_edit` concatenates videos
    1. With given 'search word' *(eg. "front")*
    2. Automatic finds all 'search words'
    3. Specific videos
- `video_edit` cuts videos to new files

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