import asyncio
from copy import deepcopy
from pathlib import Path
from typing import Any, List, Tuple

import pysrt
from bs4 import BeautifulSoup
from pysrt import SubRipFile
from tenacity import retry, stop_after_attempt, wait_random

from yuisub.llm import Translator
from yuisub.prompt import ORIGIN


def from_file(srt_path: Path | str, encoding: Any = None) -> SubRipFile:
    """
    Load srt file from file path, auto remove html tags

    :param srt_path: srt file path
    :param encoding: srt file encoding, default is utf-8
    :return:
    """
    srt = pysrt.open(path=str(srt_path), encoding=encoding)
    for sub in srt:
        try:
            soup = BeautifulSoup(sub.text, "html.parser")
            text = soup.get_text()
            sub.text = text
        except Exception as e:
            print(e)
            print(sub.text)
    return srt


@retry(wait=wait_random(min=3, max=5), stop=stop_after_attempt(5))
def bilingual(
    srt: SubRipFile, model: str, api_key: str, base_url: str, bangumi_url: str | None = None
) -> Tuple[SubRipFile, SubRipFile]:
    """
    Generate bilingual srt file, first return is the Chinese subtitle, second return is the Bilingual subtitle

    :param srt: origin srt file
    :param model: llm model
    :param api_key: llm api_key
    :param base_url: llm base_url
    :param bangumi_url: anime bangumi url
    :return:
    """

    # pending translation
    trans_list: List[str] = [s.text for s in srt]

    tr = Translator(model=model, api_key=api_key, base_url=base_url, bangumi_url=bangumi_url)
    print(tr.system_prompt)

    async def translate(index: int) -> None:
        nonlocal trans_list

        translated_text = await tr.ask(ORIGIN(origin=trans_list[index]))
        print(f"Translated: {trans_list[index]} ---> {translated_text.zh}")
        trans_list[index] = translated_text.zh

    # wait for all tasks to finish
    async def wait_tasks() -> None:
        tasks = [translate(index) for index in range(len(srt))]
        await asyncio.gather(*tasks)

    asyncio.run(wait_tasks())

    # generate bilingual srt
    srt_zh: SubRipFile = deepcopy(srt)
    srt_bilingual: SubRipFile = deepcopy(srt)
    for i, s in enumerate(srt):
        text_zh = trans_list[i]
        text_bilingual = trans_list[i] + "\n" + s.text

        srt_zh[i].text = text_zh
        srt_bilingual[i].text = text_bilingual

    return srt_zh, srt_bilingual
