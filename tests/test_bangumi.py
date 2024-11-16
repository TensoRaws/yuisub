from yuisub import bangumi


async def test_bangumi() -> None:
    url_list = [
        "https://bangumi.tv/subject/424883/",
        "https://bgm.tv/subject/424883",
        "https://bangumi.tv/subject/315574",
    ]

    for url in url_list:
        r = await bangumi(url)
        print(r.introduction)
        print(r.characters)
