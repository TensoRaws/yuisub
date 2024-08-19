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

`yuisub` can be used from the command line to generate bilingual SRT files. Here's how to use it:

```bash
yuisub -h  # Displays help message
```

### Library

`yuisub` can also be used as a library

### Example

```python3
from yuisub.srt import bilingual, from_file
from yuisub.a2t import WhisperModel

# srt from audio
model = WhisperModel(name="medium", device="cuda")
segs = model.transcribe(audio="path/to/audio.mp3")
srt = model.gen_srt(segs)

# srt from file
# srt = from_file("path/to/input.srt")

# Generate bilingual SRT
srt_zh, srt_bilingual = bilingual(
    srt=srt,
    model="gpt_model_name",
    api_key="your_openai_api_key",
    base_url="api_url",
    bangumi_url="https://bangumi.tv/subject/424883/"
)

# Save the SRT files
srt_zh.save("path/to/output.zh.srt")
srt_bilingual.save("path/to/output.bilingual.srt")
```

### License

This project is licensed under the BSD 3-Clause - see
the [LICENSE file](https://github.com/TohruskyDev/yuisub/blob/main/LICENSE) for details.
