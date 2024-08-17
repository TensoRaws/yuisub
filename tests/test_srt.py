from tests import util
from yuisub import WhisperModel


def test_srt() -> None:
    model = WhisperModel(name=util.MODEL_NAME, device=util.DEVICE)

    text, segs = model.transcribe(audio=str(util.TEST_AUDIO))
    srt = model.gen_srt(segs)

    with open(util.projectPATH / "assets" / "test.srt", "w", encoding="utf-8") as f:
        f.write(srt)
