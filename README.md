# MP4 simple editor (WIP)

**NOT FINISHED, DO NOT USE YET**

This repository contains files for my own Python MP4 video editor used to quickly cut MP4 videos and change the video volume.

Ensure you have Python 3.8 or newer with `venv`. Before running the clone, make sure that you have symlinks enabled - `git config core.symlinks true`, on Windows, Developer mode is requried (Settings -> Privacy and security -> Developer options -> Enable developer mode).

## Install (Windows)

1. `py -m venv env`
2. `.\env\Scripts\activate`
3. `py -m pip install -r requirements.txt`
4. `git submodule update --init --recursive`

## Install (Linux/MacOS)

1. `python3 -m venv env`
2. `source env/bin/activate`
3. `py -m pip install -r requirements.txt`
4. `git submodule update --init --recursive`

## Usage

Run `editor.py`.