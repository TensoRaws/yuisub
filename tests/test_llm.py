import asyncio
import os

import pytest

from tests import util
from yuisub import JP, Translator
from yuisub.llm import generate_random_str

jp = JP(
    jp="何だよ…けっこう多いじゃねぇか",
    background="彼は新しいオフィスに引っ越してきたばかりで、箱を片付け始めたところ、見たこともないような書類や物品がたくさん出てきました。「何だよ…けっこう多いじゃねぇか」と思いながら、彼は一つ一つを確認し、必要なものと不要なものを分け始めました。この量の多さには驚いたが、彼はすぐに整理整頓を始め、新しい環境に順応しようとしました。",
)


def test_llm_none() -> None:
    t = Translator(model="deepseek-chat", api_key=util.API_KEY, base_url="https://api.deepseek.com")
    print(t.system_prompt)
    res = asyncio.run(t.ask(JP(jp="", background="dfsfsaf")))
    assert res.zh == ""


@pytest.mark.skipif(os.environ.get("GITHUB_ACTIONS") == "true", reason="Skipping test when running on CI")
def test_llm() -> None:
    t = Translator(model="deepseek-chat", api_key=util.API_KEY, base_url="https://api.deepseek.com")
    print(t.system_prompt)
    res = asyncio.run(t.ask(jp))
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
    res = asyncio.run(t.ask(jp))
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
    jp_s = JP(
        jp="♪ 星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と",
        background="忍者みたいな奴だな ♪ 星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と 第1話 玄関",
    )

    res = asyncio.run(t.ask(jp_s))
    print(res.zh)


def test_random_prompt() -> None:
    s1 = generate_random_str()
    s2 = generate_random_str()
    assert s1 != s2
