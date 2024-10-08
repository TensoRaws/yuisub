from typing import Optional

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, stop_after_delay, wait_random


class BGM(BaseModel):
    introduction: str
    characters: str


@retry(wait=wait_random(min=3, max=5), stop=stop_after_delay(10) | stop_after_attempt(30))
def bangumi(url: Optional[str] = None) -> BGM:
    """
    Get anime bangumi introduction and characters info
    :param url: bangumi url
    :return:
    """
    print("Getting bangumi info...")

    if url is None or url == "":
        print("Warning: bangumi url is empty")
        return BGM(introduction="", characters="")

    anime_url = url
    if anime_url[-1] == "/":
        anime_url = anime_url[:-1]
    characters_url = anime_url + "/characters"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/58.0.3029.110 Safari/537.3"
    }

    try:
        response = requests.get(anime_url, headers=headers)
        response.encoding = "utf-8"

        if response.status_code != 200:
            print("failed to get bangumi intro info")
            raise Exception("failed to get bangumi intro info")

        soup = BeautifulSoup(response.text, "html.parser")
        intro = soup.find("div", class_="subject_summary").text.strip()

        # get characters info
        response_chars = requests.get(characters_url, headers=headers)
        response_chars.encoding = "utf-8"

        if response_chars.status_code != 200:
            print("failed to get characters info")
            raise Exception("failed to get characters info")

        soup_chars = BeautifulSoup(response_chars.text, "html.parser")

        column_div = soup_chars.find("div", id="columnInSubjectA")

        character_divs = column_div.find_all("div", class_="light_odd")

        characters: str = ""
        for character_div in character_divs:
            names = character_div.find("h2").text.strip()
            characters += str(names) + "\n"

    except Exception as e:
        print("failed to get bangumi info, retrying...")
        raise e

    return BGM(introduction=intro, characters=characters)
