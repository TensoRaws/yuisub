from typing import Optional, Tuple, Union

import numpy as np
import pysubs2
import torch
import whisper
from pysubs2 import SSAFile


class WhisperModel:
    def __init__(
        self,
        name: str = "medium",
        device: Optional[Union[str, torch.device]] = None,
        download_root: Optional[str] = None,
        in_memory: bool = False,
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
    ) -> SSAFile:
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
        return pysubs2.load_from_whisper(result)
