import argparse
import asyncio

from yuisub import SubtitleTranslator

parser = argparse.ArgumentParser(description="Generate Bilingual Subtitle from audio or subtitle file")

# Input
parser.add_argument("-a", "--AUDIO", type=str, help="Path to the audio file", required=False)
parser.add_argument("-s", "--SUB", type=str, help="Path to the input Subtitle file", required=False)
# Output
parser.add_argument("-oz", "--OUTPUT_ZH", type=str, help="Path to save the Chinese ASS file", required=False)
parser.add_argument("-ob", "--OUTPUT_BILINGUAL", type=str, help="Path to save the bilingual ASS file", required=False)
# OpenAI GPT
parser.add_argument("-om", "--OPENAI_MODEL", type=str, help="Openai model name", required=True)
parser.add_argument("-api", "--OPENAI_API_KEY", type=str, help="Openai API key", required=True)
parser.add_argument("-url", "--OPENAI_BASE_URL", type=str, help="Openai base URL", required=True)
# Bangumi
parser.add_argument("-bgm", "--BANGUMI_URL", type=str, help="Anime Bangumi URL", required=False)
parser.add_argument("-ac", "--BANGUMI_ACCESS_TOKEN", type=str, help="Anime Bangumi Access Token", required=False)
# Whisper
parser.add_argument("-d", "--TORCH_DEVICE", type=str, help="Pytorch device to use", required=False)
parser.add_argument("-wm", "--WHISPER_MODEL", type=str, help="Whisper model to use", required=False)

args = parser.parse_args()


async def _main() -> None:
    if args.AUDIO and args.SUB:
        raise ValueError("Please provide only one input file, either audio or subtitle file")

    if not args.AUDIO and not args.SUB:
        raise ValueError("Please provide an input file, either audio or subtitle file")

    if not args.OUTPUT_ZH and not args.OUTPUT_BILINGUAL:
        raise ValueError("Please provide output paths for the subtitles.")

    translator = SubtitleTranslator(
        model=args.OPENAI_MODEL,
        api_key=args.OPENAI_API_KEY,
        base_url=args.OPENAI_BASE_URL,
        bangumi_url=args.BANGUMI_URL,
        bangumi_access_token=args.BANGUMI_ACCESS_TOKEN,
        torch_device=args.TORCH_DEVICE,
        whisper_model=args.WHISPER_MODEL,
    )

    sub_zh, sub_bilingual = await translator.get_subtitles(
        sub=args.SUB,
        audio=args.AUDIO,
    )
    if args.OUTPUT_ZH:
        sub_zh.save(args.OUTPUT_ZH)
    if args.OUTPUT_BILINGUAL:
        sub_bilingual.save(args.OUTPUT_BILINGUAL)


def main() -> None:
    asyncio.run(_main())


if __name__ == "__main__":
    main()
