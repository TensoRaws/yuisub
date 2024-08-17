from pydantic import BaseModel

from yuisub.bangumi import bangumi


class JP(BaseModel):
    background: str
    jp: str


class ZH(BaseModel):
    zh: str


def anime_prompt(bangumi_url: str | None = None) -> str:
    if bangumi_url is None:
        bangumi_info = ""
    else:
        bangumi_info = bangumi(bangumi_url)

    return (
        """
下面我让你来充当一个日语翻译。你的目标是把动漫新番的日语台词翻译成中文，请翻译时不要带翻译腔，而是要翻译得自然、流畅和地道，使用贴合二次元的表达方式。
请注意，由于日语字幕是通过 AI 生成的，所以会有一些错误或者不太符合逻辑的地方，请你在翻译时尽量根据提供的 background 上下文进行翻译，保持逻辑性。
此外，我可能会给你一些动漫相关的信息，包括背景故事、人物介绍等，你需要根据这些信息进行翻译。请注意，当人名等专有名词出现时，严格按照我提供的信息进行翻译。

"""
        + bangumi_info
        + """

EXAMPLE INPUT:
{
    "background": "その重要なマラソン大会では、選手たちはすでに長い距離を走り、体力が次第に消耗しています。観客の情熱は衰えず、彼らは旗を振って、「止まるんじゃねぇぞ！」と大声で叫びます。この言葉は選手たちを励まして、疲労に耐えても諦めず、ゴールラインを突破するまで進むべきだと知らせています。この言葉は粘り強い精神を伝えるだけでなく、スポーツ競技における永遠に負けず嫌いな闘志を体現しています。"
    "jp": "止まるんじゃねぇぞ！"
}

EXAMPLE JSON OUTPUT:
{
    "zh": "不要停下来啊！"
}
"""
    )
