import os
from pathlib import Path

import torch

projectPATH = Path(__file__).resolve().parent.parent.absolute()

TEST_AUDIO = projectPATH / "assets" / "test.mp3"
TEST_ENG_SRT = projectPATH / "assets" / "eng.srt"

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODEL_NAME = "medium" if DEVICE == "cuda" else "tiny"

BANGUMI_URL = "https://bangumi.tv/subject/424883"

OPENAI_MODEL = str(os.getenv("OPENAI_MODEL")) if os.getenv("OPENAI_MODEL") else "deepseek-chat"
OPENAI_BASE_URL = str(os.getenv("OPENAI_BASE_URL")) if os.getenv("OPENAI_BASE_URL") else "https://api.deepseek.com"
OPENAI_API_KEY = str(os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else "sk-"
