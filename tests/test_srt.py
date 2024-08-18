import os

import pytest

from tests import util
from yuisub.a2t import WhisperModel
from yuisub.srt import bilingual


def test_srt() -> None:
    model = WhisperModel(name=util.MODEL_NAME, device=util.DEVICE)

    text, segs = model.transcribe(audio=str(util.TEST_AUDIO))
    srt = model.gen_srt(segs)
    srt.save(util.projectPATH / "assets" / "test.srt")


@pytest.mark.skipif(os.environ.get("GITHUB_ACTIONS") == "true", reason="Skipping test when running on CI")
def test_srt_bilingual() -> None:
    model = WhisperModel(name=util.MODEL_NAME, device=util.DEVICE)

    text, segs = model.transcribe(audio=str(util.TEST_AUDIO))
    srt = model.gen_srt(segs)
    srt_zh, srt_zh_jp = bilingual(
        srt=srt,
        model="deepseek-chat",
        api_key=util.API_KEY,
        base_url="https://api.deepseek.com",
        bangumi_url="https://bangumi.tv/subject/424883/",
    )

    srt_zh.save(util.projectPATH / "assets" / "test.zh.srt")
    srt_zh_jp.save(util.projectPATH / "assets" / "test.zh_jp.srt")
