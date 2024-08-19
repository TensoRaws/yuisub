import asyncio
from copy import deepcopy
from pathlib import Path
from typing import List

import pysubs2
from pysubs2 import Alignment, Color, SSAFile, SSAStyle
from tenacity import retry, stop_after_attempt, wait_random

from yuisub.llm import Translator
from yuisub.prompt import ORIGIN

PRESET_STYLES: dict[str, SSAStyle] = {
    "zh": SSAStyle(
        alignment=Alignment.BOTTOM_CENTER,
        primarycolor=Color(215, 215, 215),
        fontsize=18,
        fontname="Microsoft YaHei",
        bold=True,
        shadow=0,
        outline=1,
        outlinecolor=Color(198, 107, 107),
    ),
    "origin": SSAStyle(
        alignment=Alignment.BOTTOM_CENTER,
        primarycolor=pysubs2.Color(249, 246, 240),
        fontsize=10,
        fontname="Microsoft YaHei",
        shadow=0,
        outline=0.5,
    ),
}


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
def translate(
    sub: SSAFile,
    model: str,
    api_key: str,
    base_url: str,
    bangumi_url: str | None = None,
    styles: dict[str, SSAStyle] | None = None,
) -> SSAFile:
    """
    Translate subtitle file to Chinese

    :param sub: origin subtitle
    :param model: llm model
    :param api_key: llm api_key
    :param base_url: llm base_url
    :param bangumi_url: anime bangumi url
    :param styles: subtitle styles, default is PRESET_STYLES
    :return:
    """

    # pending translation
    trans_list: List[str] = [s.text for s in sub]

    tr = Translator(model=model, api_key=api_key, base_url=base_url, bangumi_url=bangumi_url)
    print(tr.system_prompt)

    async def _translate(index: int) -> None:
        nonlocal trans_list

        translated_text = await tr.ask(ORIGIN(origin=trans_list[index]))
        print(f"Translated: {trans_list[index]} ---> {translated_text.zh}")
        trans_list[index] = translated_text.zh

    # wait for all tasks to finish
    async def _wait_tasks() -> None:
        tasks = [_translate(index) for index in range(len(sub))]
        await asyncio.gather(*tasks)

    asyncio.run(_wait_tasks())

    # generate Chinese subtitle
    if styles is None:
        styles = PRESET_STYLES

    sub_zh = deepcopy(sub)
    sub_zh.styles = styles
    for i, _ in enumerate(sub):
        sub_zh[i].text = trans_list[i]
        sub_zh[i].style = "zh"

    return sub_zh


def bilingual(
    sub_origin: SSAFile,
    sub_zh: SSAFile,
    styles: dict[str, SSAStyle] | None = None,
) -> SSAFile:
    """
    Generate bilingual subtitle file

    :param sub_origin: Origin subtitle
    :param sub_zh: Chinese subtitle
    :param styles: subtitle styles, default is PRESET_STYLES
    :return:
    """

    # generate bilingual subtitle
    if styles is None:
        styles = PRESET_STYLES

    sub_bilingual = SSAFile()
    sub_bilingual.styles = styles

    for e in sub_origin:
        e.style = "origin"
        sub_bilingual.append(e)

    for e in sub_zh:
        e.style = "zh"
        sub_bilingual.append(e)

    return sub_bilingual
