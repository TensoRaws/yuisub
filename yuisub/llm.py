import json

from openai import OpenAI

from yuisub.prompt import ZH, anime_prompt


class Translator:
    def __init__(self, model: str, api_key: str, base_url: str, bangumi_url: str | None = None) -> None:
        self.model = model
        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url,
        )
        self.system_prompt = anime_prompt(bangumi_url=bangumi_url)

    def ask(self, question: str) -> ZH:
        messages = [{"role": "system", "content": self.system_prompt}, {"role": "user", "content": question}]

        response = self.client.chat.completions.create(
            model=self.model, messages=messages, response_format={"type": "json_object"}
        )

        content = json.loads(response.choices[0].message.content)

        return ZH(**content)
