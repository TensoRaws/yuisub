from tests import util
from yuisub.a2t import WhisperModel
from yuisub.srt import gen_srt, gen_srt_bilingual

# ffmpeg -i test.mkv -c:a mp3 -map 0:a:0 test.mp3


def main() -> None:
    model = WhisperModel(name="large-v2", device=util.DEVICE)

    text, segs = model.transcribe(audio=str(util.projectPATH / "assets" / "Roshidere07.mp3"))

    srt = gen_srt(segs=segs)
    with open(util.projectPATH / "assets" / "Roshidere07.srt", "w", encoding="utf-8") as f:
        f.write(srt)

    srt_zh, srt_zh_jp = gen_srt_bilingual(
        segs=segs,
        model="deepseek-chat",
        api_key=util.API_KEY,
        base_url="https://api.deepseek.com",
        bangumi_url="https://bangumi.tv/subject/424883/",
    )

    with open(util.projectPATH / "assets" / "Roshidere07.zh.srt", "w", encoding="utf-8") as f:
        f.write(srt_zh)

    with open(util.projectPATH / "assets" / "Roshidere07.zh_jp.srt", "w", encoding="utf-8") as f:
        f.write(srt_zh_jp)


if __name__ == "__main__":
    main()
