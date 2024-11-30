import os

import pytest

from yuisub.translator import SubtitleTranslator

from . import util


@pytest.mark.skipif(os.environ.get("GITHUB_ACTIONS") == "true", reason="Skipping test when running on CI")
async def test_translator_sub() -> None:
    translator = await SubtitleTranslator.load_sub(
        sub_path=str(util.TEST_ENG_SRT),
        model=util.OPENAI_MODEL,
        api_key=util.OPENAI_API_KEY,
        base_url=util.OPENAI_BASE_URL,
        bangumi_url=util.BANGUMI_URL,
        bangumi_access_token=util.BANGUMI_ACCESS_TOKEN,
    )

    sub_zh, sub_bilingual = await translator.get_subtitles()
    sub_zh.save(util.projectPATH / "assets" / "test.zh.translator.sub.ass")
    sub_bilingual.save(util.projectPATH / "assets" / "test.bilingual.translator.sub.ass")


@pytest.mark.skipif(os.environ.get("GITHUB_ACTIONS") == "true", reason="Skipping test when running on CI")
async def test_translator_audio() -> None:
    translator = await SubtitleTranslator.load_sub(
        audio_path=str(util.TEST_AUDIO),
        torch_device=util.DEVICE,
        whisper_model=util.MODEL_NAME,
        model=util.OPENAI_MODEL,
        api_key=util.OPENAI_API_KEY,
        base_url=util.OPENAI_BASE_URL,
        bangumi_url=util.BANGUMI_URL,
        bangumi_access_token=util.BANGUMI_ACCESS_TOKEN,
    )

    sub_zh, sub_bilingual = await translator.get_subtitles()
    sub_zh.save(util.projectPATH / "assets" / "test.zh.translator.audio.ass")
    sub_bilingual.save(util.projectPATH / "assets" / "test.bilingual.translator.audio.ass")
