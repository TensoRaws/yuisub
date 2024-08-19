import argparse
import sys

from yuisub.srt import bilingual, from_file

# ffmpeg -i test.mkv -c:a mp3 -map 0:a:0 test.mp3
# ffmpeg -i test.mkv -map 0:s:0 eng.srt

parser = argparse.ArgumentParser()
parser.description = "Generate bilingual SRT files from audio or SRT input."
# srt
parser.add_argument("-a", "--AUDIO", type=str, help="Path to the audio file", required=False)
parser.add_argument("-s", "--SRT", type=str, help="Path to the input SRT file", required=False)
parser.add_argument("-oz", "--OUTPUT_ZH", type=str, help="Path to save the Chinese SRT file", required=True)
parser.add_argument("-ob", "--OUTPUT_BILINGUAL", type=str, help="Path to save the bilingual SRT file", required=True)
# openai gpt
parser.add_argument("-om", "--OPENAI_MODEL", type=str, help="Openai model name", required=True)
parser.add_argument("-api", "--OPENAI_API_KEY", type=str, help="Openai API key", required=True)
parser.add_argument("-url", "--OPENAI_BASE_URL", type=str, help="Openai base URL", required=True)
# bangumi url
parser.add_argument("-bgm", "--BANGUMI_URL", type=str, help="Anime Bangumi URL", required=False)
# whisper
parser.add_argument("-d", "--TORCH_DEVICE", type=str, help="Pytorch device to use", required=False)
parser.add_argument("-wm", "--WHISPER_MODEL", type=str, help="Whisper model to use", required=False)

args = parser.parse_args()


def main() -> None:
    if args.AUDIO and args.SRT:
        raise ValueError("Please provide only one input file, either audio or SRT.")

    if args.AUDIO:
        import torch

        from yuisub.a2t import WhisperModel

        if args.TORCH_DEVICE:
            _DEVICE = args.TORCH_DEVICE
        else:
            _DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
            if sys.platform == "darwin":
                _DEVICE = "mps"

        if args.WHISPER_MODEL:
            _MODEL = args.WHISPER_MODEL
        else:
            _MODEL = "medium" if _DEVICE == "cpu" else "large-v2"

        model = WhisperModel(name=_MODEL, device=_DEVICE)

        segs = model.transcribe(audio=args.AUDIO)

        srt = model.gen_srt(segs=segs)

    else:
        srt = from_file(args.SRT)

    srt_zh, srt_bilingual = bilingual(
        srt=srt,
        model=args.OPENAI_MODEL,
        api_key=args.OPENAI_API_KEY,
        base_url=args.OPENAI_BASE_URL,
        bangumi_url=args.BANGUMI_URL,
    )

    srt_zh.save(args.OUTPUT_ZH)
    srt_bilingual.save(args.OUTPUT_BILINGUAL)


if __name__ == "__main__":
    main()
