from typing import List, Optional, Tuple, Union

import numpy as np
import pysrt
import torch
import whisper
from pydantic import BaseModel
from pysrt import SubRipFile


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
        verbose: Optional[bool] = True,
        temperature: Union[float, Tuple[float, ...]] = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0),
        compression_ratio_threshold: Optional[float] = 2.4,
        logprob_threshold: Optional[float] = -1.0,
        no_speech_threshold: Optional[float] = 0.6,
        condition_on_previous_text: bool = True,
        initial_prompt: Optional[str] = None,
        word_timestamps: bool = False,
        prepend_punctuations: str = "\"'“¿([{-",
        append_punctuations: str = "\"'.。,，!！?？:：”)]}、",
    ) -> List[Segment]:
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
        return segments

    @staticmethod
    def gen_srt(segs: List[Segment]) -> SubRipFile:
        line_out: str = ""
        for s in segs:
            segment_id = s.id + 1
            start_time = format_time(s.start)
            end_time = format_time(s.end)
            text = s.text

            line_out += f"{segment_id}\n{start_time} --> {end_time}\n{text.lstrip()}\n\n"
        subs = pysrt.from_string(line_out)
        return subs


def format_time(seconds: float) -> str:
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    milliseconds = (seconds - int(seconds)) * 1000
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d},{int(milliseconds):03d}"
