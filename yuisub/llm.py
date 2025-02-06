from typing import Optional

import openai
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_random

from yuisub.bangumi import BGM
from yuisub.prompt import ZH, anime_prompt, summary_prompt


class Translator:
    def __init__(
        self, model: str, api_key: str, base_url: str, bangumi_info: Optional[BGM] = None, summary: str = ""
    ) -> None:
        self.model = model
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self.system_prompt, self.example_input, self.example_output = anime_prompt(bangumi_info, summary)
        self.corner_case = True

    @retry(wait=wait_random(min=3, max=5), stop=stop_after_attempt(5))
    async def ask(self, question: str) -> ZH:
        if self.corner_case:
            # blank question
            if question == "":
                return ZH(zh="")

            # too long question, return directly
            if len(question) > 100:
                return ZH(zh=question)

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self.example_input},
            {"role": "assistant", "content": self.example_output},
            {"role": "user", "content": question},
        ]

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )

            zh_text = response.choices[0].message.content
            zh = ZH(zh=zh_text.strip())

        except openai.AuthenticationError as e:
            print(f"Authentication Error: {e} retrying...")
            raise e

        except openai.APIConnectionError as e:
            print(f"Connection Error: {e} retrying...")
            raise e

        except Exception as e:
            print(f"Unknown Error: {e} return original question: {question}")
            return ZH(zh=question)

        return zh


class Summarizer(Translator):
    def __init__(self, model: str, api_key: str, base_url: str, bangumi_info: Optional[BGM] = None) -> None:
        super().__init__(model, api_key, base_url, bangumi_info)
        self.system_prompt, self.example_input, self.example_output = summary_prompt(bangumi_info)
        self.corner_case = False
