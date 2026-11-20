# terminal-timecode: context for Claude

The one timecode codebase for Terminal's tools. **This repository is public:** nothing about Terminal's clients,
projects, machines, people or other software goes in it, in files, branch names or commit messages. Describe a change
only in terms of timecode itself.

- **What it does:**
  - `src/terminal_timecode/__init__.py`, on OpenTimelineIO's opentime: it refuses impossible timecodes and never guesses drop-frame.
  - `examples.json` beside it is the master list of cases.
- **Rule:** every change starts with a case in `examples.json`, then the code. After a change:
  1. run `pytest`;
  2. bump the version (`pyproject.toml` and `__version__`), tag `vX.Y.Z` and push the tag;
  3. update whatever uses the package, as `CLAUDE.local.md` lists (not in the repository). Copies of `examples.json` elsewhere are checked against this one, and their tests fail while a copy differs.
- **Check OpenTimelineIO first** before adding anything about timelines, edits or edit files. This package is for timecode only.
- Keep it boring: no dependencies beyond OpenTimelineIO, Python 3.10+, ruff with line length 120.
