# Derpibooru utils
Let's do some stuff with [Derpibooru](https://derpibooru.org/) API


## Features
1. Download Derpibooru images by search query
2. Downloading newly appeared images during repeated launches

## How to Use
1. Install python 3.11+
2. Install python packages from `requirements.txt`
I recommend using [python venv](https://docs.python.org/3/library/venv.html):
```bash
python -m venv venv
source venv/Scripts/activate
python -m pip install -r requirements.txt
```
3. Get help
```bash
python -m derp_utils -h
python -m derp_utils download -h
```
Or just download all images with query `oc:hardy` (download limit = 300 images)
```bash
python -m derp_utils download "oc:hardy" --save-tags
```
