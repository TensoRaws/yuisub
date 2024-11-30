import sys
from pathlib import Path
from typing import Any, Optional, Tuple, Union

import pysubs2

from yuisub.sub import bilingual, load, translate


class SubtitleTranslator:
    def __init__(
        self,
        model: str,
        api_key: str,
        base_url: str,
        bangumi_url: Optional[str] = None,
        bangumi_access_token: Optional[str] = None,
        torch_device: Optional[str] = None,
        whisper_model: Optional[str] = None,
    ) -> None:
        """
        Subtitle Translator

        :param model:
        :param api_key:
        :param base_url:
        :param bangumi_url:
        :param bangumi_access_token:
        :param torch_device:
        :param whisper_model:
        """
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.bangumi_url = bangumi_url
        self.bangumi_access_token = bangumi_access_token
        self.torch_device = torch_device
        self.whisper_model = whisper_model
        self.whisper_model_instance = None

        if self.whisper_model:
            import torch

            from yuisub.a2t import WhisperModel

            if self.torch_device:
                device = self.torch_device
            else:
                device = "cuda" if torch.cuda.is_available() else "cpu"
                if sys.platform == "darwin":
                    device = "mps"

            whisper_model_instance = WhisperModel(name=self.whisper_model, device=device)
            self.whisper_model_instance = whisper_model_instance

    async def get_subtitles(
        self, sub: Optional[Union[str, Path, pysubs2.SSAFile]] = None, audio: Optional[Union[str, Any]] = None
    ) -> Tuple[pysubs2.SSAFile, pysubs2.SSAFile]:
        """
        Get Subtitles from sub or audio

        :param sub:
        :param audio:
        :return: ZH Subtitles and Bilingual Subtitles
        """

        if sub:
            if isinstance(sub, (str, Path)):
                sub = load(sub)

        elif audio:
            if not self.whisper_model_instance:
                raise ValueError("Whisper model is not loaded, please initialize it first")
            sub = self.whisper_model_instance.transcribe(audio=audio)

        else:
            raise ValueError("Either audio or sub must be provided")

        sub_zh = await translate(
            sub=sub,
            model=self.model,
            api_key=self.api_key,
            base_url=self.base_url,
            bangumi_url=self.bangumi_url,
            bangumi_access_token=self.bangumi_access_token,
        )
        sub_bilingual = await bilingual(
            sub_origin=sub,
            sub_zh=sub_zh,
        )
        return sub_zh, sub_bilingual
