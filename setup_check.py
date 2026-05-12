from pathlib import Path


def _print_issue(message: str) -> None:
    print(f"- {message}")


def main() -> None:
    issues = []

    models_dir = Path("models")
    model_file = models_dir / "female.pth"
    if not models_dir.exists():
        issues.append("Create the models/ folder and add female.pth.")
    elif not model_file.exists():
        issues.append("Place female.pth in models/.")

    creds_file = Path("credentials/service_account.json")
    if not creds_file.exists():
        issues.append("Add credentials/service_account.json for Google Drive uploads.")

    try:
        import torch

        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            print(f"GPU detected: {gpu_name}")
        else:
            print("CPU mode (CUDA not available).")
    except Exception:
        issues.append("Install torch. Run: pip install -r requirements.txt")

    try:
        import rvc_python  # noqa: F401
    except Exception:
        issues.append("Install rvc-python. Run: pip install -r requirements.txt")

    import subprocess
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, timeout=5)
        if result.returncode == 0:
            print("ffmpeg detected on system.")
        else:
            issues.append(
                "ffmpeg not found. Download from https://ffmpeg.org/download.html and add to PATH."
            )
    except FileNotFoundError:
        issues.append(
            "ffmpeg not found. Download from https://ffmpeg.org/download.html and add to PATH."
        )
    except Exception:
        issues.append("Could not verify ffmpeg. Make sure it is installed and in PATH.")

    if issues:
        print("Setup issues found:")
        for issue in issues:
            _print_issue(issue)
        print("Fix the items above, then rerun: python setup_check.py")
    else:
        print("✅ All checks passed. Run: python main.py")


if __name__ == "__main__":
    main()
