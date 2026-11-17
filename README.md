# terminal-timecode

Timecode and frame numbers, both ways, strictly. A small layer over [OpenTimelineIO](https://opentimeline.io)'s
`opentime` that adds two things it leaves to its callers:

- **Timecodes that can't exist are refused.** `00:01:00;00` at 29.97 drop-frame (a number drop-frame skips), frame
  24 at 24 fps, `;` at a non-drop rate, 24 hours or more: `problem()` says why, `to_frames()` raises `ValueError`.
  OpenTimelineIO alone turns some of these into the wrong frame.
- **Drop-frame is always stated, never guessed.** OpenTimelineIO assumes drop-frame at 29.97 unless told otherwise.

```python
import terminal_timecode as tc

tc.to_frames("01:00:00:00", 23.976)  # 86400 (23.976 counts as 24)
tc.to_timecode(17982, 29.97, drop_frame=True)  # '00:10:00;00'
tc.problem("00:01:00;00", 29.97, drop_frame=True)  # 'drop-frame skips this number'
tc.frame_number("01:00:01:00", 24, start="01:00:00:00", start_number=1001)  # 1025 (VFX numbering)
```

Frame numbers count from 00:00:00:00. Rates: whole numbers, and the 1000/1001 ones (23.976, 29.97, 47.952, 59.94).
Drop-frame exists at 29.97 and 59.94 only.

## The shared examples

`src/terminal_timecode/examples.json` (also `terminal_timecode.examples()`) lists worked cases: frames ↔ timecode both
ways, typed digits and what they become, and timecodes that must be refused. It's the contract for every timecode
implementation in Terminal's tools: this package, Argento's screens (TypeScript) and TerminalPlayer's mpv script
(Lua) each run it, and their copies are checked against this one.

## Install and test

```
pip install "terminal-timecode @ https://github.com/TerminalPost/terminal-timecode/archive/refs/tags/v0.2.0.tar.gz"
pip install -e ".[test]" && pytest
```

MIT licence. Made at [Terminal](https://terminalmx.com), Mexico City.
