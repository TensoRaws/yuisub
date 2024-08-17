import asyncio
from typing import List, Optional, Tuple, Union

import numpy as np
import torch
import whisper
from pydantic import BaseModel

from yuisub.llm import Translator
from yuisub.prompt import JP


class Segment(BaseModel):
    id: int
    seek: int
    start: float
    end: float
    text: str
    tokens: List[int]
    temperature: float
    avg_logprob: float
    compression_ratio: float
    no_speech_prob: float


class WhisperModel:
    def __init__(
        self, name: str = "medium", device: str = "cuda", download_root: str | None = None, in_memory: bool = False
    ):
        self.model = whisper.load_model(name=name, device=device, download_root=download_root, in_memory=in_memory)

    def transcribe(
        self,
        audio: Union[str, np.ndarray, torch.Tensor],
        verbose: Optional[bool] = None,
        temperature: Union[float, Tuple[float, ...]] = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
        compression_ratio_threshold: Optional[float] = 2.4,
        logprob_threshold: Optional[float] = -1.0,
        no_speech_threshold: Optional[float] = 0.6,
        condition_on_previous_text: bool = True,
        initial_prompt: Optional[str] = None,
        word_timestamps: bool = False,
        prepend_punctuations: str = "\"'“¿([{-",
        append_punctuations: str = "\"'.。,，!！?？:：”)]}、",
    ) -> Tuple[str, List[Segment]]:
        result = self.model.transcribe(
            audio=audio,
            verbose=verbose,
            temperature=temperature,
            compression_ratio_threshold=compression_ratio_threshold,
            logprob_threshold=logprob_threshold,
            no_speech_threshold=no_speech_threshold,
            condition_on_previous_text=condition_on_previous_text,
            initial_prompt=initial_prompt,
            word_timestamps=word_timestamps,
            prepend_punctuations=prepend_punctuations,
            append_punctuations=append_punctuations,
        )
        segments: List[Segment] = [Segment(**seg) for seg in result["segments"]]
        return result["text"], segments

    @staticmethod
    def format_time(seconds: float) -> str:
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        milliseconds = (seconds - int(seconds)) * 1000
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{int(milliseconds):03d}"

    def gen_srt(self, segs: List[Segment]) -> str:
        line_out: str = ""
        for s in segs:
            segment_id = s.id + 1
            start_time = self.format_time(s.start)
            end_time = self.format_time(s.end)
            text = s.text

            line_out += f"{segment_id}\n{start_time} --> {end_time}\n{text.lstrip()}\n\n"
        return line_out

    def gen_srt_bilingual(
        self, segs: List[Segment], model: str, api_key: str, base_url: str, bangumi_url: str | None = None
    ) -> Tuple[str, str]:
        """
        Generate bilingual srt file, first return is the ZH subtitle, second return is the ZH-JP subtitle

        :param segs: list of Segment
        :param model: llm model
        :param api_key: llm api_key
        :param base_url: llm base_url
        :param bangumi_url: anime bangumi url
        :return:
        """

        # pending translation
        trans_list = [s.text for s in segs]

        tr = Translator(model=model, api_key=api_key, base_url=base_url, bangumi_url=bangumi_url)
        print(tr.system_prompt)

        async def translate(index: int) -> None:
            nonlocal trans_list

            if len(trans_list) < 10:
                text = " "
            elif index == 0:
                text = trans_list[0] + " " + trans_list[1] + " " + trans_list[2]
            elif index == len(trans_list) - 1:
                text = trans_list[-3] + " " + trans_list[-2] + " " + trans_list[-1]
            else:
                text = trans_list[index - 1] + " " + trans_list[index] + " " + trans_list[index + 1]

            jp = JP(jp=trans_list[index], background=text)
            translated_text = await tr.ask(jp)
            print(f"Translated: {trans_list[index]} ---> {translated_text.zh}")
            trans_list[index] = translated_text.zh

        # wait for all tasks to finish
        async def wait_tasks() -> None:
            tasks = [translate(index) for index in range(len(segs))]
            await asyncio.gather(*tasks)

        asyncio.run(wait_tasks())

        # generate bilingual srt
        line_out_zh: str = ""
        line_out_zh_jp: str = ""
        for i, s in enumerate(segs):
            segment_id = s.id + 1
            start_time = self.format_time(s.start)
            end_time = self.format_time(s.end)

            text_zh = trans_list[i]
            text_zh_jp = trans_list[i] + "\n" + s.text

            line_out_zh += f"{segment_id}\n{start_time} --> {end_time}\n{text_zh.lstrip()}\n\n"
            line_out_zh_jp += f"{segment_id}\n{start_time} --> {end_time}\n{text_zh_jp.lstrip()}\n\n"

        return line_out_zh, line_out_zh_jp
