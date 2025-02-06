import asyncio
from copy import deepcopy
from pathlib import Path
from typing import Dict, List, Optional, Union

import pysubs2
from pysubs2 import Alignment, Color, SSAEvent, SSAFile, SSAStyle
from tenacity import retry, stop_after_attempt, wait_random

from yuisub.bangumi import bangumi
from yuisub.llm import Summarizer, Translator

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
    "ad": SSAStyle(
        alignment=Alignment.TOP_CENTER,
        primarycolor=Color(215, 215, 215),
        fontsize=10,
        fontname="Microsoft YaHei",
        shadow=0.5,
        outline=1,
        outlinecolor=Color(198, 107, 107),
    ),
}


def advertisement(ad: Optional[str] = None, start: int = 0, end: int = 5000) -> SSAEvent:
    """
    Add advertisement to subtitle

    :param ad: advertisement
    :param start: start time, ms
    :param end: end time, ms
    :return:
    """
    if ad is None:
        ad = "本字幕由 TensoRaws 提供, 使用 LLM 翻译 \\N 请遵循 CC BY-NC-SA 4.0 协议使用"

    sub_ad = SSAEvent()
    sub_ad.start = start
    sub_ad.end = end
    sub_ad.text = ad
    sub_ad.style = "ad"

    return sub_ad


def load(sub_path: Union[Path, str], encoding: str = "utf-8") -> SSAFile:
    """
    Load subtitle from file path, default encoding is utf-8 and remove style

    :param sub_path: subtitle file path
    :param encoding: subtitle file encoding, default is utf-8
    :return:
    """
    sub = pysubs2.load(str(sub_path), encoding=encoding)
    return sub


@retry(wait=wait_random(min=3, max=5), stop=stop_after_attempt(5))
async def translate(
    sub: SSAFile,
    model: str,
    api_key: str,
    base_url: str,
    bangumi_url: Optional[str] = None,
    bangumi_access_token: Optional[str] = None,
    styles: Optional[Dict[str, SSAStyle]] = None,
    ad: Optional[SSAEvent] = advertisement(),  # noqa: B008
) -> SSAFile:
    """
    Translate subtitle file to Chinese

    :param sub: origin subtitle
    :param model: llm model
    :param api_key: llm api_key
    :param base_url: llm base_url
    :param bangumi_url: anime bangumi url
    :param bangumi_access_token: anime bangumi access token
    :param styles: subtitle styles, default is PRESET_STYLES
    :param ad: add advertisement to subtitle, default is TensoRaws
    :return:
    """
    # pending translation
    trans_list: List[str] = [s.text for s in sub]

    # get bangumi info asynchronously
    bangumi_info = await bangumi(bangumi_url, bangumi_access_token) if bangumi_url else None

    # initialize summarizer
    summarizer = Summarizer(
        model=model,
        api_key=api_key,
        base_url=base_url,
        bangumi_info=bangumi_info,
    )
    print(summarizer.system_prompt)

    # get summary
    summary = await summarizer.ask("\n".join(trans_list))

    # initialize translator
    translator = Translator(
        model=model,
        api_key=api_key,
        base_url=base_url,
        bangumi_info=bangumi_info,
        summary=summary.zh,
    )
    print(translator.system_prompt)

    # create translate text task
    async def _translate(index: int) -> None:
        nonlocal trans_list
        translated_text = await translator.ask(trans_list[index])
        print(f"Translated: {trans_list[index]} ---> {translated_text.zh}")
        trans_list[index] = translated_text.zh

    # start translation tasks
    tasks = [_translate(i) for i in range(len(sub))]
    await asyncio.gather(*tasks)

    # gen Chinese subtitle
    if styles is None:
        styles = PRESET_STYLES

    sub_zh = SSAFile()
    sub_zh.styles = styles

    # add advertisement
    if ad:
        sub_zh.append(ad)

    # copy origin subtitle and replace text with translated text
    sub_temp = deepcopy(sub)
    for i, e in enumerate(sub_temp):
        e.style = "zh"
        e.text = trans_list[i]
        sub_zh.append(e)

    return sub_zh


async def bilingual(
    sub_origin: SSAFile,
    sub_zh: SSAFile,
    styles: Optional[Dict[str, SSAStyle]] = None,
) -> SSAFile:
    """
    Generate bilingual subtitle file asynchronously

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

    # notice: deepcopy is necessary for the zh subtitle if you wanna edit it in bilingual!
    for e in sub_zh:
        sub_bilingual.append(e)

    return sub_bilingual
