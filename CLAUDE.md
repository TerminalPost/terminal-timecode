# terminal-timecode: context for Claude

The one timecode codebase for Terminal's tools (owner Joakim Ziegler's decision, 2026-11-17): Argento (private,
`~/Documents/dev/argento`) and TerminalPlayer (`~/Documents/dev/TerminalPlayer`, GPL later) both use it. **This
repository is public:** nothing about Terminal's clients, projects, machines or people goes in it.

- **What it does:**
  - `src/terminal_timecode/__init__.py`, on OpenTimelineIO's opentime: it refuses impossible timecodes and never guesses drop-frame.
  - `examples.json` beside it is the master list of cases.
- **Rule:** every change starts with a case in `examples.json`, then the code. After a change:
  1. run `pytest`;
  2. bump the version (`pyproject.toml` and `__version__`), tag `vX.Y.Z` and push the tag;
  3. update the pinned tag in Argento's `requirements.txt`;
  4. copy `examples.json` to Argento's `core/display/timecode_examples.json` and to TerminalPlayer's `tests/timecode_examples.json`, then run their checks. Their tests fail while a copy differs.
- **Check OpenTimelineIO first** before adding anything about timelines, edits or edit files. This package is for timecode only.
- Keep it boring: no dependencies beyond OpenTimelineIO, Python 3.10+, ruff with line length 120.
