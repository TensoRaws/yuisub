from yuisub import bangumi


def test_bangumi() -> None:
    url_list = [
        "https://bangumi.tv/subject/424883/",
        "https://bgm.tv/subject/424883",
        "https://bangumi.tv/subject/315574",
    ]

    for url in url_list:
        r = bangumi(url)
        print(r)
