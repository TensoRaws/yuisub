# yuisub

[![codecov](https://codecov.io/gh/TensoRaws/yuisub/branch/main/graph/badge.svg?token=B2TNKYN4O4)](https://codecov.io/gh/TensoRaws/yuisub)
[![CI-test](https://github.com/TensoRaws/yuisub/actions/workflows/CI-test.yml/badge.svg)](https://github.com/TensoRaws/yuisub/actions/workflows/CI-test.yml)
[![Release-pypi](https://github.com/TensoRaws/yuisub/actions/workflows/Release-pypi.yml/badge.svg)](https://github.com/TensoRaws/yuisub/actions/workflows/Release-pypi.yml)
[![PyPI version](https://badge.fury.io/py/yuisub.svg)](https://badge.fury.io/py/yuisub)
![GitHub](https://img.shields.io/github/license/TensoRaws/yuisub)

Auto translation of new anime episodes based on ~~Yui-MHCP001~~ LLM

### Install

Make sure you have Python >= 3.9 installed on your system

```bash
pip install yuisub
```

If you wanna use the `a2t` module, you need to install `Whisper` first

```bash
# pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install openai-whisper
```

### Command Line Usage

`yuisub` can be used from the command line to generate bilingual ASS files. Here's how to use it:

```bash
yuisub -h  # Displays help message
```

### Library

`yuisub` can also be used as a library

### Example

```python3
import asyncio

from yuisub.sub import translate, bilingual, load
from yuisub.a2t import WhisperModel

# Using an asynchronous environment
async def main() -> None:

    # Using subtitle file input
    sub = load("path/to/sub.srt")

    # Or using audio input
    # model = WhisperModel(name="medium", device="cuda")
    # sub = model.transcribe(audio="path/to/audio.mp3")

    # generate bilingual subtitle
    sub_zh = await translate(
        sub=sub,
        model="gpt_model_name",
        api_key="your_openai_api_key",
        base_url="api_url",
        bangumi_url="https://bangumi.tv/subject/424883/"
        bangumi_access_token='your_bangumi_token'
    )

    sub_bilingual = await bilingual(
        sub_origin=sub,
        sub_zh=sub_zh
    )

    # save the ASS files
    sub_zh.save("path/to/output_zh.ass")
    sub_bilingual.save("path/to/output_bilingual.ass")

asyncio.run(main())
```

Here is a complete example of how to use the SubtitleTranslator class in a script:

```python3
import asyncio

from yuisub.translator import SubtitleTranslator

# Using an asynchronous environment
async def main() -> None:

    translator = await SubtitleTranslator.load_sub(

        # Using subtitle file input
        sub_path='path/to/sub.srt',

        # Or using audio input
        # audio_path='path/to/audio.mp3',
        # torch_device='cuda',
        # whisper_model='medium',

        model='gpt_model_name',
        api_key='your_openai_api_key',
        base_url='api_url',
        bangumi_url='https://bangumi.tv/subject/424883/',
        bangumi_access_token='your_bangumi_token'
    )

    sub_zh, sub_bilingual = await translator.get_subtitles()
    sub_zh.save('path/to/output_zh.ass')
    sub_bilingual.save('path/to/output_bilingual.ass')

asyncio.run(main())
```

### License

This project is licensed under the BSD 3-Clause - see
the [LICENSE file](https://github.com/TohruskyDev/yuisub/blob/main/LICENSE) for details.
