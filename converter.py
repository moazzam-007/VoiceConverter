import logging
import time
from pathlib import Path

import torch
from rvc_python.infer import RVCInference


class VoiceConverter:
    def __init__(self, model_path: Path, pitch_shift: int, device: str = "cuda:0") -> None:
        self.model_path = model_path
        self.pitch_shift = pitch_shift
        self.device = device
        self._rvc = self._load_model()

    def _create_rvc(self) -> RVCInference:
        device = self.device
        if device.startswith("cuda") and not torch.cuda.is_available():
            logging.warning("CUDA not available, falling back to CPU.")
            device = "cpu"

        try:
            return RVCInference(device=device)
        except Exception as exc:
            if device != "cpu":
                logging.warning("CUDA init failed (%s). Falling back to CPU.", device)
                try:
                    return RVCInference(device="cpu")
                except Exception as cpu_exc:
                    raise RuntimeError(
                        "CUDA not available and CPU fallback failed."
                    ) from cpu_exc
            raise RuntimeError("Failed to initialize RVC inference.") from exc

    def _load_model(self) -> RVCInference:
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}")

        rvc = self._create_rvc()
        rvc.load_model(str(self.model_path))
        logging.info("Model loaded: %s", self.model_path)
        return rvc

    def convert_file(self, input_path: Path, output_path: Path) -> Path:
        output_path = output_path.with_suffix(".wav")
        logging.info("Conversion started: %s", input_path)
        self._rvc.params["f0_up_key"] = self.pitch_shift
        start = time.perf_counter()

        try:
            self._rvc.infer_file(str(input_path), str(output_path))
        except Exception as exc:
            raise RuntimeError(f"Conversion failed for {input_path}") from exc

        elapsed = time.perf_counter() - start
        logging.info("Conversion done: %s (%.2fs)", output_path, elapsed)
        return output_path
