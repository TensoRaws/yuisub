import asyncio
import os

import pytest

from tests import util
from yuisub import ORIGIN, Translator

origin = ORIGIN(
    origin="何だよ…けっこう多いじゃねぇか",
)


def test_llm_none() -> None:
    t = Translator(model="deepseek-chat", api_key=util.API_KEY, base_url="https://api.deepseek.com")
    print(t.system_prompt)
    res = asyncio.run(t.ask(ORIGIN(origin="")))
    assert res.zh == ""


@pytest.mark.skipif(os.environ.get("GITHUB_ACTIONS") == "true", reason="Skipping test when running on CI")
def test_llm() -> None:
    t = Translator(model="deepseek-chat", api_key=util.API_KEY, base_url="https://api.deepseek.com")
    print(t.system_prompt)
    res = asyncio.run(t.ask(origin))
    print(res.zh)


@pytest.mark.skipif(os.environ.get("GITHUB_ACTIONS") == "true", reason="Skipping test when running on CI")
def test_llm_bangumi() -> None:
    t = Translator(
        model="deepseek-chat",
        api_key=util.API_KEY,
        base_url="https://api.deepseek.com",
        bangumi_url="https://bangumi.tv/subject/424883/",
    )
    print(t.system_prompt)
    res = asyncio.run(t.ask(origin))
    print(res.zh)


@pytest.mark.skipif(os.environ.get("GITHUB_ACTIONS") == "true", reason="Skipping test when running on CI")
def test_llm_bangumi_2() -> None:
    t = Translator(
        model="deepseek-chat",
        api_key=util.API_KEY,
        base_url="https://api.deepseek.com",
        bangumi_url="https://bangumi.tv/subject/424883/",
    )
    print(t.system_prompt)
    s = ORIGIN(
        origin="♪ 星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と",
    )

    res = asyncio.run(t.ask(s))
    print(res.zh)
