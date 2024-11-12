import asyncio
import os

import pytest

from tests import util
from yuisub import ORIGIN, Summarizer, Translator, bangumi

origin = ORIGIN(
    origin="何だよ…けっこう多いじゃねぇか",
)

summary_origin = ORIGIN(
    origin="""
May I ask your name, miss?
Seriously, you stop that right now!
Uh... your grandfather seems very spry.
So, you're Kuze-kun?
That's me. Nice to meet you.
Would you be Alisa-san's mother?
My, such a polite young boy.
Nice to meet you too. I'm Kujo Akemi, Alisa's mother.
She's told me lots about you.
Good things, I hope.
Oh, she positively beams when talking about you.
Does she now?
Miss.
Would you like to join our family?
H-Huh?
Hey, behave!
What do you say to marrying my boy Masachika here?
Shut your damn mouth!
Is that all right with you, Masachika?
Again, shut up.
So?
Are you going to marry Kuze-kun?
Quiet, Mom.
We'll be going now.
Thank you for your time.
"""
)


def test_llm_none() -> None:
    t = Translator(model=util.OPENAI_MODEL, api_key=util.OPENAI_API_KEY, base_url=util.OPENAI_BASE_URL)
    print(t.system_prompt)
    res = asyncio.run(t.ask(ORIGIN(origin="")))
    assert res.zh == ""


@pytest.mark.skipif(os.environ.get("GITHUB_ACTIONS") == "true", reason="Skipping test when running on CI")
def test_llm() -> None:
    t = Translator(
        model=util.OPENAI_MODEL,
        api_key=util.OPENAI_API_KEY,
        base_url=util.OPENAI_BASE_URL,
    )
    print(t.system_prompt)
    res = asyncio.run(t.ask(origin))
    print(res.zh)


@pytest.mark.skipif(os.environ.get("GITHUB_ACTIONS") == "true", reason="Skipping test when running on CI")
def test_llm_bangumi() -> None:
    t = Translator(
        model=util.OPENAI_MODEL,
        api_key=util.OPENAI_API_KEY,
        base_url=util.OPENAI_BASE_URL,
        bangumi_info=asyncio.run(bangumi(util.BANGUMI_URL)),
    )
    print(t.system_prompt)
    res = asyncio.run(t.ask(origin))
    print(res.zh)


@pytest.mark.skipif(os.environ.get("GITHUB_ACTIONS") == "true", reason="Skipping test when running on CI")
def test_llm_bangumi_2() -> None:
    t = Translator(
        model=util.OPENAI_MODEL,
        api_key=util.OPENAI_API_KEY,
        base_url=util.OPENAI_BASE_URL,
        bangumi_info=asyncio.run(bangumi(util.BANGUMI_URL)),
    )
    print(t.system_prompt)
    s = ORIGIN(
        origin="♪ 星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と星と",
    )

    res = asyncio.run(t.ask(s))
    print(res.zh)


@pytest.mark.skipif(os.environ.get("GITHUB_ACTIONS") == "true", reason="Skipping test when running on CI")
def test_llm_summary() -> None:
    t = Summarizer(
        model=util.OPENAI_MODEL,
        api_key=util.OPENAI_API_KEY,
        base_url=util.OPENAI_BASE_URL,
        bangumi_info=asyncio.run(bangumi(util.BANGUMI_URL)),
    )
    print(t.system_prompt)
    res = asyncio.run(t.ask(summary_origin))
    print(res.zh)
