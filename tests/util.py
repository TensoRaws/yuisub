from pathlib import Path

import torch

projectPATH = Path(__file__).resolve().parent.parent.absolute()

TEST_AUDIO = projectPATH / "assets" / "test.mp3"
TEST_ENG_SRT = projectPATH / "assets" / "eng.srt"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_NAME = "medium" if DEVICE == "cuda" else "tiny"

API_KEY = "sk-"
