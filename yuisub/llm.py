import json

import openai
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_random

from yuisub.prompt import ORIGIN, ZH, anime_prompt, summary_prompt


class Translator:
    def __init__(self, model: str, api_key: str, base_url: str, bangumi_info: str = "", summary: str = "") -> None:
        self.model = model
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self.system_prompt = anime_prompt(bangumi_info, summary)
        self.corner_case = True

    @retry(wait=wait_random(min=3, max=5), stop=stop_after_attempt(5))
    async def ask(self, question: ORIGIN) -> ZH:
        if self.corner_case:
            # blank question
            if question.origin == "":
                return ZH(zh="")

            # too long question, return directly
            if len(question.origin) > 100:
                return ZH(zh=question.origin)

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": question.model_dump_json()},
        ]

        try:
            response = await self.client.chat.completions.create(
                model=self.model, messages=messages, response_format={"type": "json_object"}
            )
            content = json.loads(response.choices[0].message.content)
            zh = ZH(**content)

        except openai.AuthenticationError as e:
            print(f"Authentication Error: {e} retrying...")
            raise e

        except openai.APIConnectionError as e:
            print(f"Connection Error: {e} retrying...")
            raise e

        except Exception as e:
            print(f"Unknown Error: {e} return original question: {question.origin}")
            return ZH(zh=question.origin)

        return zh


class Summarizer(Translator):
    def __init__(self, model: str, api_key: str, base_url: str, bangumi_info: str = "") -> None:
        super().__init__(model, api_key, base_url, bangumi_info)
        self.system_prompt = summary_prompt(bangumi_info)
        self.corner_case = False
