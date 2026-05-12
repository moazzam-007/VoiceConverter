import logging
import time
from pathlib import Path
from typing import Iterable

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from config import INPUT_FOLDER, OUTPUT_FOLDER, MODEL_PATH, PITCH_SHIFT, DEVICE
from converter import VoiceConverter
from uploader import upload_file


ALLOWED_EXTENSIONS = {".wav", ".mp3", ".flac", ".m4a", ".ogg"}


def _setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def _iter_audio_files(folder: Path) -> Iterable[Path]:
    for path in folder.iterdir():
        if path.is_file() and path.suffix.lower() in ALLOWED_EXTENSIONS:
            yield path


def _wait_for_file_ready(path: Path, attempts: int = 10, delay: float = 2.0) -> bool:
    last_size = -1
    for _ in range(attempts):
        if not path.exists():
            return False
        size = path.stat().st_size
        if size > 0 and size == last_size:
            return True
        last_size = size
        time.sleep(delay)
    return False


def _process_file(converter: VoiceConverter, input_path: Path) -> None:
    if input_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        return

    if not _wait_for_file_ready(input_path):
        logging.warning("Skipping unreadable file: %s", input_path)
        return

    output_path = OUTPUT_FOLDER / (input_path.stem + ".wav")
    if output_path.exists():
        logging.info("Output exists, skipping: %s", output_path)
        return

    converter.convert_file(input_path, output_path)
    link = upload_file(output_path)
    logging.info("Shareable link: %s", link)


def _process_batch(converter: VoiceConverter) -> None:
    logging.info("Starting batch processing in %s", INPUT_FOLDER)
    for audio_file in _iter_audio_files(INPUT_FOLDER):
        _process_file(converter, audio_file)
    logging.info("Batch processing complete.")


class _InputHandler(FileSystemEventHandler):
    def __init__(self, converter: VoiceConverter) -> None:
        self.converter = converter

    def on_created(self, event):
        if event.is_directory:
            return
        _process_file(self.converter, Path(event.src_path))

    def on_moved(self, event):
        if event.is_directory:
            return
        _process_file(self.converter, Path(event.dest_path))


def main() -> None:
    _setup_logging()
    INPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)

    logging.info("Loading RVC model: %s", MODEL_PATH)
    converter = VoiceConverter(MODEL_PATH, PITCH_SHIFT, DEVICE)

    _process_batch(converter)

    logging.info("Watching input folder for new files...")
    observer = Observer()
    observer.schedule(_InputHandler(converter), str(INPUT_FOLDER), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Stopping watcher.")
        observer.stop()

    observer.join()


if __name__ == "__main__":
    main()
