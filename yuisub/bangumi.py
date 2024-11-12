# bangumi.py

import asyncio
import re
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel

# 使用信号量限制并发请求数
SEMAPHORE_LIMIT = 32


@dataclass
class Character:
    id: int
    name: str
    chinese_name: Optional[str] = None


class BGM(BaseModel):
    introduction: str
    characters: str


async def extract_bangumi_id(url: str) -> Optional[str]:
    """从Bangumi URL中提取番剧ID"""
    pattern = r"(?:https?://)?(?:www\.)?(?:bangumi\.tv|bgm\.tv)/subject/(\d+)"
    match = re.search(pattern, url)
    return match.group(1) if match else None


def construct_api_url(bangumi_id: str) -> str:
    """根据番剧ID构建API URL"""
    return f"https://api.bgm.tv/v0/subjects/{bangumi_id}"


async def get_character_info(
    client: httpx.AsyncClient, character: Dict[str, Any], semaphore: asyncio.Semaphore
) -> Character:
    """获取单个角色的详细信息"""
    async with semaphore:
        char_id = character["id"]
        char_name = character["name"]
        url = f"https://api.bgm.tv/v0/characters/{char_id}"

        response = await client.get(url)
        if response.status_code != 200:
            return Character(id=char_id, name=char_name)

        data = response.json()
        chinese_name = None

        for info in data.get("infobox", []):
            if info["key"] == "简体中文名":
                chinese_name = info["value"]
                break

        return Character(id=char_id, name=char_name, chinese_name=chinese_name)


async def fetch_bangumi_data(client: httpx.AsyncClient, url: str) -> tuple[str, List[Dict[str, Any]]]:
    """获取番剧基本信息和角色列表"""
    bangumi_id = await extract_bangumi_id(url)
    if not bangumi_id:
        raise ValueError("Invalid bangumi URL")

    api_url = construct_api_url(bangumi_id)
    chars_url = f"{api_url}/characters"

    # 并发请求番剧信息和角色列表
    response_info, response_chars = await asyncio.gather(client.get(api_url), client.get(chars_url))

    if response_info.status_code != 200 or response_chars.status_code != 200:
        raise Exception("Failed to fetch bangumi data")

    return response_info.json()["summary"], response_chars.json()


async def bangumi(url: Optional[str] = None) -> BGM:
    """
    异步获取番剧信息和角色列表

    Args:
        url: Bangumi URL

    Returns:
        BGM object containing introduction and characters info
    """
    print("Getting bangumi info...")

    if not url:
        print("Warning: bangumi url is empty")
        return BGM(introduction="", characters="")

    # 去除URL末尾的"/"
    if url[-1] == "/":
        url = url[:-1]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "*/*",
        "Host": "api.bgm.tv",
        "Connection": "keep-alive",
    }

    async with httpx.AsyncClient(headers=headers, timeout=30.0) as client:
        try:
            # 获取基本信息和角色列表
            if url:
                introduction, characters_data = await fetch_bangumi_data(client, url)
            else:
                raise ValueError("Invalid bangumi URL")

            # 创建信号量控制并发请求数
            semaphore = asyncio.Semaphore(SEMAPHORE_LIMIT)

            # 并发获取所有角色的详细信息
            character_tasks = [get_character_info(client, char, semaphore) for char in characters_data]
            characters_info = await asyncio.gather(*character_tasks)

            # 格式化角色信息
            characters_text = ""
            for char in characters_info:
                if char.chinese_name:
                    characters_text += f"{char.name} / {char.chinese_name}\n"
                else:
                    characters_text += f"{char.name}\n"

            return BGM(introduction=introduction, characters=characters_text)

        except Exception as e:
            print(f"Error fetching bangumi info: {e}")
            raise


async def main() -> None:
    """
    Main function for testing bangumi functionality
    """
    url = "https://bangumi.tv/subject/315574"
    start_time = time.time()
    result = await bangumi(url)
    use_time = time.time() - start_time
    print(f"Introduction:\n{result.introduction[:100]}...")
    print(f"Characters:\n{result.characters}")
    print(f"Use time: {use_time}")


if __name__ == "__main__":
    asyncio.run(main())
