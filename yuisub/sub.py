import asyncio
from copy import deepcopy
from pathlib import Path
from typing import Dict, List, Optional, Union

import pysubs2
from pysubs2 import Alignment, Color, SSAEvent, SSAFile, SSAStyle
from tenacity import retry, stop_after_attempt, wait_random

from yuisub.bangumi import bangumi
from yuisub.llm import Summarizer, Translator
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


async def load(sub_path: Union[Path, str], encoding: str = "utf-8") -> SSAFile:
    """
    异步加载字幕文件

    Load subtitle from file path, default encoding is utf-8 and remove style

    :param sub_path: subtitle file path
    :param encoding: subtitle file encoding, default is utf-8
    :return:
    """
    # 由于pysubs2.load本身是同步的, 我们使用线程池来避免阻塞
    return await asyncio.to_thread(pysubs2.load, str(sub_path), encoding=encoding)


@retry(wait=wait_random(min=3, max=5), stop=stop_after_attempt(5))
async def translate(
    sub: SSAFile,
    model: str,
    api_key: str,
    base_url: str,
    bangumi_url: Optional[str] = None,
    styles: Optional[Dict[str, SSAStyle]] = None,
    ad: Optional[SSAEvent] = advertisement(),  # noqa: B008
) -> SSAFile:
    """
    异步翻译字幕文件

    :param sub: 原始字幕
    :param model: LLM模型
    :param api_key: API密钥
    :param base_url: API基础URL
    :param bangumi_url: bangumi URL
    :param styles: 字幕样式
    :param ad: 广告信息
    :return: 翻译后的字幕文件

    Translate subtitle file to Chinese

    :param sub: origin subtitle
    :param model: llm model
    :param api_key: llm api_key
    :param base_url: llm base_url
    :param bangumi_url: anime bangumi url
    :param styles: subtitle styles, default is PRESET_STYLES
    :param ad: add advertisement to subtitle, default is TensoRaws
    :return:
    """
    try:
        # 获取待翻译的文本列表
        trans_list: List[str] = [s.text for s in sub]

        # 异步获取bangumi信息
        bangumi_info = await bangumi(bangumi_url) if bangumi_url else None

        # 初始化总结器
        summarizer = Summarizer(
            model=model,
            api_key=api_key,
            base_url=base_url,
            bangumi_info=bangumi_info,
        )

        print("Summarizing...")
        # 获取总结
        summary = await summarizer.ask(ORIGIN(origin="\n".join(trans_list)))

        # 初始化翻译器
        translator = Translator(
            model=model,
            api_key=api_key,
            base_url=base_url,
            bangumi_info=bangumi_info,
            summary=summary.zh,
        )
        print(translator.system_prompt)

        # 创建翻译任务
        async def translate_text(index: int) -> None:
            nonlocal trans_list
            translated_text = await translator.ask(ORIGIN(origin=trans_list[index]))
            print(f"Translated: {trans_list[index]} ---> {translated_text.zh}")
            trans_list[index] = translated_text.zh

        # 并发执行翻译任务
        tasks = [translate_text(i) for i in range(len(sub))]
        await asyncio.gather(*tasks)

        # 生成中文字幕
        if styles is None:
            styles = PRESET_STYLES

        sub_zh = SSAFile()
        sub_zh.styles = styles

        # 添加广告
        if ad:
            sub_zh.append(ad)

        # 复制并更新字幕
        sub_temp = deepcopy(sub)
        for i, e in enumerate(sub_temp):
            e.style = "zh"
            e.text = trans_list[i]
            sub_zh.append(e)

        return sub_zh

    except Exception as e:
        print(f"Translation error: {e}")
        raise


async def bilingual(
    sub_origin: SSAFile,
    sub_zh: SSAFile,
    styles: Optional[Dict[str, SSAStyle]] = None,
) -> SSAFile:
    """
    异步生成双语字幕

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

    # notice: deepcopy is necessary for the zh subtitle if you wanna edit it in bilingual!
    for e in sub_zh:
        sub_bilingual.append(e)

    return sub_bilingual


# 使用示例
async def main() -> None:
    # 加载字幕
    sub = await load("path/to/subtitle.ass")

    # 翻译字幕
    translated_sub = await translate(
        sub=sub, model="your-model", api_key="your-api-key", base_url="your-base-url", bangumi_url="your-bangumi-url"
    )

    # 生成双语字幕
    bilingual_sub = await bilingual(sub, translated_sub)

    # 保存字幕
    await asyncio.to_thread(bilingual_sub.save, "output.ass")


if __name__ == "__main__":
    asyncio.run(main())
