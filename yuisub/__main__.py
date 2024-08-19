from tests import util
from yuisub.a2t import WhisperModel
from yuisub.srt import bilingual

# ffmpeg -i test.mkv -c:a mp3 -map 0:a:0 test.mp3
# ffmpeg -i test.mkv -map 0:s:0 eng.srt


def main() -> None:
    model = WhisperModel(name="large-v2", device=util.DEVICE)

    text, segs = model.transcribe(audio=str(util.projectPATH / "assets" / "Roshidere07.mp3"))

    srt = model.gen_srt(segs=segs)
    srt.save(util.projectPATH / "assets" / "Roshidere07.srt")

    srt_zh, srt_zh_jp = bilingual(
        srt=srt,
        model="deepseek-chat",
        api_key=util.API_KEY,
        base_url="https://api.deepseek.com",
        bangumi_url="https://bangumi.tv/subject/424883/",
    )

    srt_zh.save(util.projectPATH / "assets" / "Roshidere07.zh.srt")
    srt_zh_jp.save(util.projectPATH / "assets" / "Roshidere07.zh_jp.srt")


if __name__ == "__main__":
    main()
