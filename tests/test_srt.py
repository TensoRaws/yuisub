from tests import util
from yuisub import WhisperModel


def test_srt() -> None:
    model = WhisperModel()

    srt = model.gen_srt(str(util.TEST_AUDIO))

    with open(util.projectPATH / "assets" / "test.srt", "w", encoding="utf-8") as f:
        f.write(srt)
