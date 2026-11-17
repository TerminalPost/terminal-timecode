"""Timecode and frame numbers, both ways, strictly: one codebase for Terminal's tools (Argento, TerminalPlayer).

Built on OpenTimelineIO's `opentime` (ASWF, Apache-2.0), adding what it leaves to its callers:
- timecodes that can't exist are refused: OpenTimelineIO quietly turns 00:01:00;00 at 29.97 drop-frame, a number
  drop-frame skips, into the wrong frame (1798);
- drop-frame is always stated, never guessed: OpenTimelineIO assumes drop-frame at 29.97 unless told otherwise.

Every function here passes every case in `examples.json` (frames both ways, refused timecodes). Other implementations
(Argento's screens in TypeScript, TerminalPlayer's mpv script in Lua) keep a copy of that file and must pass it too.

    >>> to_frames("01:00:00:00", 24)
    86400
    >>> to_timecode(17982, 29.97, drop_frame=True)
    '00:10:00;00'
    >>> problem("00:01:00;00", 29.97, drop_frame=True)
    'drop-frame skips this number'
"""

import json
import re
from importlib import resources

import opentimelineio.opentime as otio_time

__version__ = "0.1.0"
__all__ = ["exact_rate", "examples", "problem", "skipped_per_minute", "to_frames", "to_timecode"]

SHAPE = re.compile(r"^(\d\d):(\d\d):(\d\d)([:;])(\d\d)$")


def exact_rate(fps: float) -> float:
    """The exact rate for a nominal one: 23.976 is 24000/1001, 29.97 is 30000/1001, 59.94 is 60000/1001."""
    whole = round(fps)
    if whole > 0 and abs(fps - whole) < 1e-6:
        return float(whole)
    if whole > 0 and abs(fps - whole * 1000 / 1001) < 0.01:
        return whole * 1000 / 1001
    raise ValueError(f"{fps} fps isn't a frame rate timecode knows")


def skipped_per_minute(fps: float, drop_frame: bool) -> int:
    """How many frame numbers drop-frame skips each minute: 2 at 29.97, 4 at 59.94, 0 otherwise."""
    whole = round(fps)
    return whole // 15 if drop_frame and whole in (30, 60) and exact_rate(fps) != whole else 0


def problem(value: str, fps: float, drop_frame: bool = False) -> str | None:
    """Why a timecode can't exist at this rate, or None if it can. Strict: two digits per field, ';' exactly when
    drop-frame, no number drop-frame skips, below 24 hours. Lenient typing (1:0:0:0, 01000000) is the caller's job."""
    match = SHAPE.match(value or "")
    if not match:
        return "not HH:MM:SS:FF"
    h, m, s, f = (int(match[i]) for i in (1, 2, 3, 5))
    skipped = skipped_per_minute(fps, drop_frame)
    if drop_frame and not skipped:
        return "no drop-frame at this rate"
    if (match[4] == ";") != drop_frame:
        return "drop-frame needs ';'" if drop_frame else "';' means drop-frame"
    if h > 23 or m > 59 or s > 59:
        return "hours, minutes or seconds too high"
    if f >= round(fps):
        return "frames too high for this rate"
    if skipped and s == 0 and m % 10 and f < skipped:
        return "drop-frame skips this number"
    return None


def to_frames(value: str, fps: float, drop_frame: bool = False) -> int:
    """A timecode to its frame number counted from 00:00:00:00. Refuses one that can't exist (ValueError)."""
    why = problem(value, fps, drop_frame)
    if why:
        raise ValueError(f"{value} at {fps} fps: {why}")
    return otio_time.from_timecode(value, exact_rate(fps)).to_frames()


def to_timecode(frames: int, fps: float, drop_frame: bool = False) -> str:
    """A frame number counted from 00:00:00:00 to its timecode (wrapping at 24 hours). Refuses negative frames."""
    if drop_frame and not skipped_per_minute(fps, drop_frame):
        raise ValueError(f"{fps} fps has no drop-frame timecode")
    if frames < 0:
        raise ValueError("frame numbers start at 0")
    rate = exact_rate(fps)
    return otio_time.to_timecode(otio_time.RationalTime(frames, rate), rate, drop_frame)


def examples() -> dict:
    """The shared examples (`examples.json`): "frames", "typed" and "refused" cases, with an "about" text."""
    return json.loads(resources.files(__package__).joinpath("examples.json").read_text(encoding="utf-8"))
