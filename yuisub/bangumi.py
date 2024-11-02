from typing import Optional

import requests
import re
import threading
from pydantic import BaseModel
from tenacity import retry, stop_after_attempt, stop_after_delay, wait_random

characters: str = ""
lock = threading.RLock()

class BGM(BaseModel):
    introduction: str
    characters: str

def extract_bangumi_id(url):
    """
    从Bangumi URL中提取番剧ID

    Args:
        url: Bangumi番剧的URL

    Returns:
        番剧ID，如果未找到则返回None
    """

    # 正则表达式匹配番剧ID
    pattern = r"https://bangumi.tv/subject/(\d+)"
    match = re.search(pattern, url)

    if match:
        return match.group(1)
    else:
        return None

def construct_api_url(bangumi_id):
    """
    根据番剧ID构建API URL

    Args:
        bangumi_id: 番剧ID

    Returns:
        API URL
    """

    return f"https://api.bgm.tv/v0/subjects/{bangumi_id}"

def get_characters(character, headers):
    ids = character["id"]
    names = character["name"]
    global characters, lock
    #构造角色详细信息API URL
    characters_info_url = "https://api.bgm.tv/v0/characters/" + str(ids)

    #请求角色详细信息API
    response_chars_info = requests.get(characters_info_url, headers=headers)
    response_chars_info.encoding = "utf-8"

    if response_chars_info.status_code != 200:
        print("failed to get characters info")
        raise Exception("failed to get characters info")
            
    #解析API返回的数据
    """ 返回的数据格式如下
    {
        "id": 0,
        "name": "string",
        "type": 1,
        "images": {
            "large": "string",
            "medium": "string",
            "small": "string",
            "grid": "string"
        },
        "summary": "string",
        "locked": true,
        "infobox": [
            {
                "key": "简体中文名",
                "value": "菜月昴"
            }
        ],
        "gender": "string",
        "blood_type": 1,
        "birth_year": 0,
        "birth_mon": 0,
        "birth_day": 0,
        "stat": {
        "comments": 0,
        "collects": 0
        }
    }
    """
    #获取infobox中的简体中文名
    data_chars_info = response_chars_info.json()
    for infobox in data_chars_info["infobox"]:
        if infobox["key"] == "简体中文名":
            #组合角色简体中文名
            with lock:
                characters += f"{names} / {infobox['value']}\n"
            break
        else:
            with lock:
                characters += f"{names}\n"
            break

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


    #此处保留原方法
    #因为直接使用API请求到的数据不全，没有简体中文名
    #如果使用API遍历角色ID获取简体中文名，会导致请求次数过多，降低性能
    
    """
    anime_url = url
    if anime_url[-1] == "/":
        anime_url = anime_url[:-1]
    characters_url = anime_url + "/characters"
    """

    #对输入的URL进行处理，获取番剧ID
    #例如：https://bangumi.tv/subject/425998 为输入的URL
    #则获取的番剧ID为425998
    #所对应的API URL为：https://api.bgm.tv/v0/subjects/425998
    #所对应的角色API URL为：https://api.bgm.tv/v0/subjects/425998/characters

    #去除URL末尾的"/"
    if url[-1] == "/":
        url = url[:-1]
    #构建API URL
    bangumi_id = extract_bangumi_id(url)
    api_url = construct_api_url(bangumi_id)
    #构建characters_id_url
    characters_id_url = api_url + "/characters"


    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': '*/*',
        'Host': 'api.bgm.tv',
        'Connection': 'keep-alive',
    }

    try:
        #此处保留原方法
        """
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
        """

        #使用API获取summary数据
        response = requests.get(api_url, headers=headers)
        response.encoding = "utf-8"

        if response.status_code != 200:
            print("failed to get bangumi info")
            raise Exception("failed to get bangumi info")
        
        #解析API返回的数据
        data = response.json()
        intro = data["summary"]

        #获取角色信息
        response_chars = requests.get(characters_id_url, headers=headers)
        response_chars.encoding = "utf-8"

        if response_chars.status_code != 200:
            print("failed to get characters info")
            raise Exception("failed to get characters info")
        
        #解析API返回的数据
        """ 返回的数据格式如下
        [
           {
                "id": 0,
                "name": "string",
                "type": 1,
                "images": {
                    "large": "string",
                    "medium": "string",
                    "small": "string",
                    "grid": "string"
                },
                "relation": "string",
                "actors": []
            }
        ]
        """

        #获取ID
        #获取角色简体中文名的方式
        #1.遍历角色ID，获取角色信息
        #2.请求角色信息API，获取角色简体中文名
        #角色详细信息API地址，例如：https://api.bgm.tv/v0/characters/35607
        #其中35607为角色ID和name
        data_chars = response_chars.json()
        
        #使用多线程来加速
        threads = []
        for character in data_chars:
            thread = threading.Thread(target=get_characters, args=(character, headers))
            threads.append(thread)
            thread.start()
            
        for thread in threads:
            thread.join()

    except Exception as e:
        print("failed to get bangumi info, retrying...")
        raise e

    return BGM(introduction=intro, characters=characters)
