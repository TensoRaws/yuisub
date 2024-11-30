import sys
from pathlib import Path
from typing import Optional, Tuple, Union

import pysubs2

from yuisub.sub import bilingual, load, translate


class SubtitleTranslator:
    def __init__(
        self,
        sub: pysubs2.SSAFile,
        model: str,
        api_key: str,
        base_url: str,
        bangumi_url: Optional[str] = None,
        bangumi_access_token: Optional[str] = None,
    ) -> None:
        self.sub = sub
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
        self.bangumi_url = bangumi_url
        self.bangumi_access_token = bangumi_access_token

    @classmethod
    async def load_sub(
        cls,
        model: str,
        api_key: str,
        base_url: str,
        sub_path: Optional[Union[str, Path, pysubs2.SSAFile]] = None,
        audio_path: Optional[Union[str, Path]] = None,
        bangumi_url: Optional[str] = None,
        bangumi_access_token: Optional[str] = None,
        torch_device: Optional[str] = None,
        whisper_model: Optional[str] = None,
    ) -> "SubtitleTranslator":
        if audio_path:
            import torch

            from yuisub.a2t import WhisperModel

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
            sub = whisper_model_instance.transcribe(audio=str(audio_path))
        elif sub_path:
            if isinstance(sub_path, (str, Path)):
                sub = load(sub_path)
            elif isinstance(sub_path, pysubs2.SSAFile):
                sub = sub_path

        return cls(
            sub=sub,
            model=model,
            api_key=api_key,
            base_url=base_url,
            bangumi_url=bangumi_url,
            bangumi_access_token=bangumi_access_token,
        )

    async def get_subtitles(self) -> Tuple[pysubs2.SSAFile, pysubs2.SSAFile]:
        sub_zh = await translate(
            sub=self.sub,
            model=self.model,
            api_key=self.api_key,
            base_url=self.base_url,
            bangumi_url=self.bangumi_url,
            bangumi_access_token=self.bangumi_access_token,
        )
        sub_bilingual = await bilingual(
            sub_origin=self.sub,
            sub_zh=sub_zh,
        )
        return sub_zh, sub_bilingual
