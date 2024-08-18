import asyncio
from typing import List, Tuple

from tenacity import retry, stop_after_attempt, wait_random

from yuisub.a2t import Segment
from yuisub.llm import Translator
from yuisub.prompt import ORIGIN


def format_time(seconds: float) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    milliseconds = (seconds - int(seconds)) * 1000
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{int(milliseconds):03d}"


def gen_srt(segs: List[Segment]) -> str:
    line_out: str = ""
    for s in segs:
        segment_id = s.id + 1
        start_time = format_time(s.start)
        end_time = format_time(s.end)
        text = s.text

        line_out += f"{segment_id}\n{start_time} --> {end_time}\n{text.lstrip()}\n\n"
    return line_out


@retry(wait=wait_random(min=3, max=5), stop=stop_after_attempt(5))
def gen_srt_bilingual(
    segs: List[Segment], model: str, api_key: str, base_url: str, bangumi_url: str | None = None
) -> Tuple[str, str]:
    """
    Generate bilingual srt file, first return is the ZH subtitle, second return is the ZH-JP subtitle

    :param segs: list of Segment
    :param model: llm model
    :param api_key: llm api_key
    :param base_url: llm base_url
    :param bangumi_url: anime bangumi url
    :return:
    """

    # pending translation
    trans_list = [s.text for s in segs]

    tr = Translator(model=model, api_key=api_key, base_url=base_url, bangumi_url=bangumi_url)
    print(tr.system_prompt)

    async def translate(index: int) -> None:
        nonlocal trans_list

        translated_text = await tr.ask(ORIGIN(origin=trans_list[index]))
        print(f"Translated: {trans_list[index]} ---> {translated_text.zh}")
        trans_list[index] = translated_text.zh

    # wait for all tasks to finish
    async def wait_tasks() -> None:
        tasks = [translate(index) for index in range(len(segs))]
        await asyncio.gather(*tasks)

    asyncio.run(wait_tasks())

    # generate bilingual srt
    line_out_zh: str = ""
    line_out_zh_jp: str = ""
    for i, s in enumerate(segs):
        segment_id = s.id + 1
        start_time = format_time(s.start)
        end_time = format_time(s.end)

        text_zh = trans_list[i]
        text_zh_jp = trans_list[i] + "\n" + s.text

        line_out_zh += f"{segment_id}\n{start_time} --> {end_time}\n{text_zh.lstrip()}\n\n"
        line_out_zh_jp += f"{segment_id}\n{start_time} --> {end_time}\n{text_zh_jp.lstrip()}\n\n"

    return line_out_zh, line_out_zh_jp
