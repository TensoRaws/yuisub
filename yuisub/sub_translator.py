import sys
from typing import Optional

import pysubs2
import torch

from yuisub.a2t import WhisperModel
from yuisub.prompt import PRESET_STYLES
from yuisub.sub import bilingual, load, translate


class SubtitleTranslator:
    def __init__(
        self,
        sub: pysubs2.SSAFile,
        openai_model: str,
        openai_api_key: str,
        openai_base_url: str,
        bangumi_url: Optional[str] = None,
        bangumi_access_token: Optional[str] = None,
    ) -> None:
        self.sub = sub
        self.openai_model = openai_model
        self.openai_api_key = openai_api_key
        self.openai_base_url = openai_base_url
        self.bangumi_url = bangumi_url
        self.bangumi_access_token = bangumi_access_token
        self.sub_zh = None
        self.sub_bilingual = None

    @classmethod
    async def from_audio(
        cls,
        audio_path: str,
        openai_model: str,
        openai_api_key: str,
        openai_base_url: str,
        bangumi_url: Optional[str] = None,
        bangumi_access_token: Optional[str] = None,
        torch_device: Optional[str] = None,
        whisper_model: Optional[str] = None,
    ) -> "SubtitleTranslator":
        if torch_device:
            device = torch_device
        else:
            device = "cuda" if torch.cuda.is_available() else "cpu"
            if sys.platform == "darwin":
                device = "mps"

        if whisper_model:
            model_name = whisper_model
        else:
            model_name = "medium" if device == "cpu" else "large-v2"

        whisper_model_instance = WhisperModel(name=model_name, device=device)
        sub = whisper_model_instance.transcribe(audio=audio_path)
        return cls(
            sub=sub,
            openai_model=openai_model,
            openai_api_key=openai_api_key,
            openai_base_url=openai_base_url,
            bangumi_url=bangumi_url,
            bangumi_access_token=bangumi_access_token,
        )

    @classmethod
    async def from_sub(
        cls,
        sub_path: str,
        openai_model: str,
        openai_api_key: str,
        openai_base_url: str,
        bangumi_url: Optional[str] = None,
        bangumi_access_token: Optional[str] = None,
    ) -> "SubtitleTranslator":
        sub = load(sub_path)
        return cls(
            sub=sub,
            openai_model=openai_model,
            openai_api_key=openai_api_key,
            openai_base_url=openai_base_url,
            bangumi_url=bangumi_url,
            bangumi_access_token=bangumi_access_token,
        )

    async def translate(self) -> None:
        self.sub_zh = await translate(
            sub=self.sub,
            model=self.openai_model,
            api_key=self.openai_api_key,
            base_url=self.openai_base_url,
            bangumi_url=self.bangumi_url,
            bangumi_access_token=self.bangumi_access_token,
            styles=PRESET_STYLES,
        )
        self.sub_bilingual = await bilingual(
            sub_origin=self.sub,
            sub_zh=self.sub_zh,
            styles=PRESET_STYLES,
        )
