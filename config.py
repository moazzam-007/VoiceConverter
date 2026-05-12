from pathlib import Path

MODEL_PATH = Path("models/female.pth")
DEVICE = "cuda:0"  # Change to "cpu" if no GPU
PITCH_SHIFT = 12
INPUT_FOLDER = Path("input")
OUTPUT_FOLDER = Path("output")

SERVICE_ACCOUNT_FILE = Path("credentials/service_account.json")
DRIVE_FOLDER_ID = "REPLACE_WITH_DRIVE_FOLDER_ID"
