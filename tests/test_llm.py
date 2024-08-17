import os

import pytest

from tests import util
from yuisub import JP, Translator


@pytest.mark.skipif(os.environ.get("GITHUB_ACTIONS") == "true", reason="Skipping test when running on CI")
def test_llm() -> None:
    t = Translator(model="deepseek-chat", api_key=util.API_KEY, base_url="https://api.deepseek.com")
    print(t.system_prompt)

    jp = JP(
        jp="何だよ…けっこう多いじゃねぇか",
        background="彼は新しいオフィスに引っ越してきたばかりで、箱を片付け始めたところ、見たこともないような書類や物品がたくさん出てきました。「何だよ…けっこう多いじゃねぇか」と思いながら、彼は一つ一つを確認し、必要なものと不要なものを分け始めました。この量の多さには驚いたが、彼はすぐに整理整頓を始め、新しい環境に順応しようとしました。",
    )
    res = t.ask(str(jp))
    print(res.zh)
