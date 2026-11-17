"""Every case in examples.json must hold. The "typed" cases are for typing fields, which this package doesn't have."""

import doctest

import pytest

import terminal_timecode as tc

EXAMPLES = tc.examples()


def label(case: dict) -> str:
    return f"{case['timecode'] or 'empty'}@{case['fps']}{'df' if case['drop_frame'] else ''}"


@pytest.mark.parametrize("case", EXAMPLES["frames"], ids=label)
def test_frames_and_timecode_both_ways(case):
    assert tc.to_timecode(case["frames"], case["fps"], case["drop_frame"]) == case["timecode"]
    assert tc.problem(case["timecode"], case["fps"], case["drop_frame"]) is None
    assert tc.to_frames(case["timecode"], case["fps"], case["drop_frame"]) == case["frames"]


@pytest.mark.parametrize("case", EXAMPLES["refused"], ids=label)
def test_impossible_timecodes_are_refused(case):
    assert tc.problem(case["timecode"], case["fps"], case["drop_frame"])
    with pytest.raises(ValueError):
        tc.to_frames(case["timecode"], case["fps"], case["drop_frame"])


def test_every_frame_round_trips_at_drop_frame_rates():
    for fps in (29.97, 59.94):
        for frames in range(0, 2 * 3600 * 60, 37):
            assert tc.to_frames(tc.to_timecode(frames, fps, True), fps, True) == frames


def test_drop_frame_is_never_guessed():
    # OpenTimelineIO alone would write 00:01:00;02 here: at 29.97 it assumes drop-frame unless told.
    assert tc.to_timecode(1800, 29.97) == "00:01:00:00"


def test_what_timecode_doesnt_know_is_refused():
    for call in (
        lambda: tc.to_timecode(0, 26.5),
        lambda: tc.to_timecode(0, 24, drop_frame=True),
        lambda: tc.to_timecode(-1, 24),
        lambda: tc.exact_rate(0),
    ):
        with pytest.raises(ValueError):
            call()


def test_the_examples_in_the_docstring():
    assert doctest.testmod(tc).failed == 0
