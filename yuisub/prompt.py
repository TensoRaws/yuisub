from typing import Optional, Tuple

from pydantic import BaseModel

from yuisub.bangumi import BGM


class ZH(BaseModel):
    zh: str


def anime_prompt(bangumi_info: Optional[BGM] = None, summary: str = "") -> Tuple[str, str, str]:
    if bangumi_info is None:
        bangumi_info = BGM(introduction="", characters="")

    system_prompt = (
        "你的目标是把这集新番的台词翻译成中文，要翻译得自然、流畅和地道，使用贴合二次元的表达方式。\n"
        "字幕可能是通过 AI 生成的，请你在翻译时尽量保持逻辑性和连贯性。\n"
        "此外，我可能会给你一些动漫相关的信息和本集的剧情总结。请注意，当人名等专有名词出现时，严格按照我提供的信息进行翻译。\n\n"
        "角色列表（日/中）：\n"
        f"{bangumi_info.characters}\n\n"
        "本集简介：\n"
        f"{summary}"
    ).strip()

    example_input = "止まるんじゃねぇぞ！"
    example_output = "不要停下来啊！"

    return system_prompt, example_input, example_output


def summary_prompt(bangumi_info: Optional[BGM] = None) -> Tuple[str, str, str]:
    if bangumi_info is None:
        bangumi_info = BGM(introduction="", characters="")

    system_prompt = (
        "你的目标是用中文总结这集新番的剧情，要求简洁明了，不要遗漏重要的细节。\n"
        "我会给你一整集新番的台词，你需要根据这段台词总结出剧情的主要内容。\n"
        "此外，我会提供给你一些动漫相关的信息，帮助你更好地理解剧情。请注意，当人名等专有名词出现时，严格按照我提供的信息总结。\n\n"
        "动漫简介：\n"
        f"{bangumi_info.introduction}\n\n"
        "角色列表（日/中）：\n"
        f"{bangumi_info.characters}"
    ).strip()

    example_input = "It is... How do you know that? I think you mentioned it in your introduction when you transferred in. Anyway, that's not important. My birthday is April 9th. I've already turned sixteen. I've already turned sixteen. Anyway, thanks for checking in, Alya. See you tomorrow."
    example_output = "在这部动漫新番中，主角久世政近的邻座是一个名叫艾莉莎的女孩。艾莉莎通常对政近表现出冷漠的态度，但有时她会用俄语小声地向他撒娇。政近实际上拥有母语级别的俄语听力，能够理解艾莉莎的话，但他选择装作听不懂。艾莉莎误以为政近不懂俄语，所以她才会在他面前展示出她真实的一面。两人之间有着一种甜蜜的氛围，但他们都试图隐藏这一点。在对话中，艾莉莎纠正了政近关于她生日的错误认知，告诉他她的生日是4月9日，并且她已经16岁了。这段对话增加了他们之间的亲密感，让人对他们的关系发展充满期待。"

    return system_prompt, example_input, example_output
