# Voice Conversion Automation

Fully automated male-to-female voice conversion pipeline.

## Requirements

- Python 3.10
- NVIDIA GPU recommended
- ffmpeg installed on the system

## Setup steps

1. Install dependencies:
	pip install -r requirements.txt
2. Download a female RVC model (.pth) from AI Hub Discord and place it in models/.
3. Set up a Google Drive service account and place the JSON in credentials/.
4. Edit config.py with your DRIVE_FOLDER_ID.
5. Run the setup check:
	python setup_check.py
6. Run the pipeline:
	python main.py

## How it works

input/ folder -> RVC conversion -> output/ folder -> Google Drive upload -> link printed in logs

## Supported audio formats

wav, mp3, flac, m4a, ogg
