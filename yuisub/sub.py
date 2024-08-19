import asyncio
from copy import deepcopy
from pathlib import Path
from typing import List, Tuple

import pysubs2
from pysubs2 import Alignment, Color, SSAFile, SSAStyle
from tenacity import retry, stop_after_attempt, wait_random

from yuisub.llm import Translator
from yuisub.prompt import ORIGIN


def load(sub_path: Path | str, encoding: str = "utf-8") -> SSAFile:
    """
    Load subtitle from file path, default encoding is utf-8 and remove style

    :param sub_path: subtitle file path
    :param encoding: subtitle file encoding, default is utf-8
    :return:
    """
    sub = pysubs2.load(str(sub_path), encoding=encoding)
    return sub


@retry(wait=wait_random(min=3, max=5), stop=stop_after_attempt(5))
def bilingual(
    sub: SSAFile, model: str, api_key: str, base_url: str, bangumi_url: str | None = None
) -> Tuple[SSAFile, SSAFile]:
    """
    Generate bilingual subtitle file, first return is the Chinese subtitle, second return is the Bilingual subtitle

    :param sub: origin subtitle
    :param model: llm model
    :param api_key: llm api_key
    :param base_url: llm base_url
    :param bangumi_url: anime bangumi url
    :return:
    """

    # pending translation
    trans_list: List[str] = [s.text for s in sub]

    tr = Translator(model=model, api_key=api_key, base_url=base_url, bangumi_url=bangumi_url)
    print(tr.system_prompt)

    async def translate(index: int) -> None:
        nonlocal trans_list

        translated_text = await tr.ask(ORIGIN(origin=trans_list[index]))
        print(f"Translated: {trans_list[index]} ---> {translated_text.zh}")
        trans_list[index] = translated_text.zh

    # wait for all tasks to finish
    async def wait_tasks() -> None:
        tasks = [translate(index) for index in range(len(sub))]
        await asyncio.gather(*tasks)

    asyncio.run(wait_tasks())

    # generate Chinese subtitle
    sub_zh = deepcopy(sub)
    for i, _ in enumerate(sub):
        sub_zh[i].text = trans_list[i]

    # generate bilingual subtitle
    sub_bilingual = SSAFile()
    sub_bilingual.styles = {
        "bottom": SSAStyle(alignment=Alignment.BOTTOM_CENTER, primarycolor=Color(255, 255, 0)),
        "top": SSAStyle(alignment=Alignment.TOP_CENTER, primarycolor=pysubs2.Color(0, 128, 128)),
    }
    for e in sub:
        e.style = "bottom"
        sub_bilingual.append(e)
    for e in sub_zh:
        e.style = "top"
        sub_bilingual.append(e)

    return sub_zh, sub_bilingual
