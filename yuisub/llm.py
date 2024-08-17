import json

from openai import AsyncOpenAI

from yuisub.prompt import JP, ZH, anime_prompt


class Translator:
    def __init__(self, model: str, api_key: str, base_url: str, bangumi_url: str | None = None) -> None:
        self.model = model
        self.client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self.system_prompt = anime_prompt(bangumi_url=bangumi_url)

    async def ask(self, question: JP) -> ZH:
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": question.model_dump_json()},
        ]

        response = await self.client.chat.completions.create(
            model=self.model, messages=messages, response_format={"type": "json_object"}
        )

        content = json.loads(response.choices[0].message.content)

        return ZH(**content)
