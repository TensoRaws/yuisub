import os

import pytest

from tests import util
from yuisub import WhisperModel


def test_srt() -> None:
    model = WhisperModel(name=util.MODEL_NAME, device=util.DEVICE)

    text, segs = model.transcribe(audio=str(util.TEST_AUDIO))
    srt = model.gen_srt(segs)

    with open(util.projectPATH / "assets" / "test.srt", "w", encoding="utf-8") as f:
        f.write(srt)


@pytest.mark.skipif(os.environ.get("GITHUB_ACTIONS") == "true", reason="Skipping test when running on CI")
def test_srt_bilingual() -> None:
    model = WhisperModel(name=util.MODEL_NAME, device=util.DEVICE)

    text, segs = model.transcribe(audio=str(util.TEST_AUDIO))
    srt_zh, srt_zh_jp = model.gen_srt_bilingual(
        segs=segs,
        model="deepseek-chat",
        api_key=util.API_KEY,
        base_url="https://api.deepseek.com",
        bangumi_url="https://bangumi.tv/subject/424883/",
    )

    with open(util.projectPATH / "assets" / "test.zh.srt", "w", encoding="utf-8") as f:
        f.write(srt_zh)

    with open(util.projectPATH / "assets" / "test.zh_jp.srt", "w", encoding="utf-8") as f:
        f.write(srt_zh_jp)
