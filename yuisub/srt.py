import asyncio
from copy import deepcopy
from typing import Tuple

from pysrt import SubRipFile
from tenacity import retry, stop_after_attempt, wait_random

from yuisub.llm import Translator
from yuisub.prompt import ORIGIN


def format_time(seconds: float) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    milliseconds = (seconds - int(seconds)) * 1000
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{int(milliseconds):03d}"


@retry(wait=wait_random(min=3, max=5), stop=stop_after_attempt(5))
def bilingual(
    srt: SubRipFile, model: str, api_key: str, base_url: str, bangumi_url: str | None = None
) -> Tuple[SubRipFile, SubRipFile]:
    """
    Generate bilingual srt file, first return is the ZH subtitle, second return is the ZH-JP subtitle

    :param srt: origin srt file
    :param model: llm model
    :param api_key: llm api_key
    :param base_url: llm base_url
    :param bangumi_url: anime bangumi url
    :return:
    """

    # pending translation
    trans_list = [s.text for s in srt]

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
    line_out_zh: SubRipFile = deepcopy(srt)
    line_out_zh_jp: SubRipFile = deepcopy(srt)
    for i, s in enumerate(srt):
        text_zh = trans_list[i]
        text_zh_jp = trans_list[i] + "\n" + s.text

        line_out_zh[i].text = text_zh
        line_out_zh_jp[i].text = text_zh_jp

    return line_out_zh, line_out_zh_jp
