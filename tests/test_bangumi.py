from yuisub import bangumi

from . import util


async def test_bangumi() -> None:
    url_list = [
        "https://bangumi.tv/subject/424883/",
        "https://bgm.tv/subject/424883",
        "https://bangumi.tv/subject/315574",
    ]

    for url in url_list:
        r = await bangumi(url=url, token=util.BANGUMI_ACCESS_TOKEN)
        print(r.introduction)
        print(r.characters)
