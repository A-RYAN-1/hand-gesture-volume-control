# Recorded hands

Two compact files of labelled hand landmarks, used to fit and to report the mute (fist) classifier.

| File | Hands | From | Used for |
|---|---|---|---|
| `hagrid-fit.json.gz` | 2,482 | HaGRID `ann_subsample`, every hand | fitting the two thresholds (`tools/fit_fist.py`) |
| `hagrid-test.json.gz` | 3,223 | HaGRID `ann_test`, 150 photos per gesture, seed 12, none shared with the fit file | the reported numbers (`tools/evaluate_gestures.py`) |

Each entry is a gesture label and MediaPipe's 21 landmarks as fractions of the photo, rounded to 4 decimals. No
image, box or person id is kept. `no_gesture` hands are other people's hands at rest in the same photos.
Rebuild with `tools/build_hagrid_set.py` from the annotation files of the Kaggle dataset `kapitanov/hagrid`.

**Source and licence.** HaGRID, the HAnd Gesture Recognition Image Dataset, by Alexander Kapitanov, Karina
Kvanchiani, Alexander Nagaev, Roman Kraynov and Andrei Makhliarchuk, https://github.com/hukenovs/hagrid,
licensed under Creative Commons Attribution-ShareAlike 4.0 (https://creativecommons.org/licenses/by-sa/4.0/).
These two files are an adapted subset (landmarks and labels only) and are shared under the same licence. The
rest of this repository is not covered by that licence.

**Limit.** The landmarks are fractions of photos whose size is not recorded, so a ratio of distances carries the
photo's aspect ratio, and photos are not webcam video: per-frame rates here are not false mutes per minute.
