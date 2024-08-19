import os

import pytest

from tests import util
from yuisub.a2t import WhisperModel
from yuisub.sub import bilingual, load


def test_sub() -> None:
    sub = load(util.TEST_ENG_SRT)
    sub.save(util.projectPATH / "assets" / "test.en.ass")


def test_audio() -> None:
    model = WhisperModel(name=util.MODEL_NAME, device=util.DEVICE)

    sub = model.transcribe(audio=str(util.TEST_AUDIO))
    sub.save(util.projectPATH / "assets" / "test.audio.ass")


@pytest.mark.skipif(os.environ.get("GITHUB_ACTIONS") == "true", reason="Skipping test when running on CI")
def test_bilingual() -> None:
    sub = load(util.TEST_ENG_SRT)

    sub_zh, sub_bilingual = bilingual(
        sub=sub,
        model=util.OPENAI_MODEL,
        api_key=util.OPENAI_API_KEY,
        base_url=util.OPENAI_BASE_URL,
        bangumi_url=util.BANGUMI_URL,
    )

    sub_zh.save(util.projectPATH / "assets" / "test.zh.ass")
    sub_bilingual.save(util.projectPATH / "assets" / "test.bilingual.ass")
