from pydantic import BaseModel

from yuisub.bangumi import bangumi


class ORIGIN(BaseModel):
    origin: str


class ZH(BaseModel):
    zh: str


def anime_prompt(bangumi_url: str | None = None) -> str:
    if bangumi_url is None:
        bangumi_info = ""
    else:
        bangumi_info = bangumi(bangumi_url)

    return (
        """
            你的目标是把动漫新番的台词翻译成中文，要翻译得自然、流畅和地道，使用贴合二次元的表达方式。
            请注意，由于字幕可能是通过 AI 生成的，所以会有一些错误的地方，请你在翻译时尽量保持逻辑性。
            此外，我可能会给你一些动漫相关的信息。请注意，当人名等专有名词出现时，严格按照我提供的信息进行翻译。

            """
        + bangumi_info
        + """

EXAMPLE INPUT:
{
    "origin": "止まるんじゃねぇぞ！"
}

EXAMPLE JSON OUTPUT:
{
    "zh": "不要停下来啊！"
}
"""
    )
