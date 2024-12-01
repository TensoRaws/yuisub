import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple, Union

import pysubs2

from yuisub.sub import advertisement, bilingual, load, translate


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
        Subtitle Translator Class

        :param model: llm model name
        :param api_key: llm api key
        :param base_url: llm base url
        :param bangumi_url: bangumi url
        :param bangumi_access_token: bangumi access token
        :param torch_device: torch device
        :param whisper_model: whisper model name
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
                try:
                    device = "cuda" if torch.cuda.is_available() else "cpu"
                    if sys.platform == "darwin":
                        device = "mps" if torch.backends.mps.is_available() else "cpu"
                except Exception:
                    print("torch device failed to auto select, using cpu instead")
                    device = "cpu"

            whisper_model_instance = WhisperModel(name=self.whisper_model, device=device)
            self.whisper_model_instance = whisper_model_instance

    async def get_subtitles(
        self,
        sub: Optional[Union[str, Path, pysubs2.SSAFile]] = None,
        audio: Optional[Union[str, Any]] = None,
        styles: Optional[Dict[str, pysubs2.SSAStyle]] = None,
        ad: Optional[pysubs2.SSAEvent] = advertisement(),  # noqa: B008
    ) -> Tuple[pysubs2.SSAFile, pysubs2.SSAFile]:
        """
        Get Translated Subtitles and Bilingual Subtitles from Subtitle or Audio

        :param sub: subtitle file path or pysubs2.SSAFile
        :param audio: audio file path or numpy array or torch tensor
        :param styles: subtitle styles, default is PRESET_STYLES
        :param ad: ad: add advertisement to subtitle, default is TensoRaws
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
            styles=styles,
            ad=ad,
        )
        sub_bilingual = await bilingual(
            sub_origin=sub,
            sub_zh=sub_zh,
        )
        return sub_zh, sub_bilingual
