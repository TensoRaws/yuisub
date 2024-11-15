import os

import pytest

from tests import util
from yuisub.a2t import WhisperModel
from yuisub.sub import bilingual, load, translate


def test_sub() -> None:
    sub = load(util.TEST_ENG_SRT)
    sub.save(util.projectPATH / "assets" / "test.en.ass")


def test_audio() -> None:
    model = WhisperModel(name=util.MODEL_NAME, device=util.DEVICE)

    sub = model.transcribe(audio=str(util.TEST_AUDIO))
    sub.save(util.projectPATH / "assets" / "test.audio.ass")


async def test_bilingual() -> None:
    sub = load(util.TEST_ENG_SRT)
    await bilingual(sub, sub)


@pytest.mark.skipif(os.environ.get("GITHUB_ACTIONS") == "true", reason="Skipping test when running on CI")
async def test_bilingual_2() -> None:
    sub = load(util.TEST_ENG_SRT)

    sub_zh = await translate(
        sub=sub,
        model=util.OPENAI_MODEL,
        api_key=util.OPENAI_API_KEY,
        base_url=util.OPENAI_BASE_URL,
        bangumi_url=util.BANGUMI_URL,
    )
    sub_bilingual = await bilingual(sub_origin=sub, sub_zh=sub_zh)

    sub_zh.save(util.projectPATH / "assets" / "test.zh.ass")
    sub_bilingual.save(util.projectPATH / "assets" / "test.bilingual.ass")
