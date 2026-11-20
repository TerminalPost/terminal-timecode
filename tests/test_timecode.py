"""Every case in examples.json must hold."""

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


@pytest.mark.parametrize("case", EXAMPLES["typed"], ids=lambda c: f"{c['digits']}@{c['fps']}")
def test_typed_digits_become_a_timecode_that_exists(case):
    result = tc.typed(case["digits"], case["fps"], case["drop_frame"])
    assert result == case["timecode"]
    assert tc.problem(result, case["fps"], case["drop_frame"]) is None


@pytest.mark.parametrize("case", EXAMPLES["pasted"], ids=lambda c: f"{c['text']!r}@{c['fps']}")
def test_pasted_text_becomes_a_timecode_that_exists(case):
    result = tc.typed(case["text"], case["fps"], case["drop_frame"])
    assert result == case["timecode"]
    assert tc.problem(result, case["fps"], case["drop_frame"]) is None


def test_typed_text_without_a_digit_is_refused():
    for text in ("", "   ", "::", "abc", None):
        with pytest.raises(ValueError):
            tc.typed(text, 24)
    with pytest.raises(ValueError):
        tc.typed("01000000", 24, drop_frame=True)


def test_any_eight_digits_give_a_timecode_that_exists():
    for fps, drop in ((24, False), (23.976, False), (25, False), (29.97, True), (29.97, False), (59.94, True)):
        for n in range(0, 100_000_000, 104_729):
            assert tc.problem(tc.typed(f"{n:08d}", fps, drop), fps, drop) is None


@pytest.mark.parametrize(
    "case", EXAMPLES["numbered"], ids=lambda c: f"{c['timecode']}@{c['start']}={c['start_number']}"
)
def test_frame_numbers_from_a_chosen_start_both_ways(case):
    rate = (case["fps"], case["drop_frame"])
    assert tc.frame_number(case["timecode"], *rate, case["start"], case["start_number"]) == case["number"]
    assert tc.from_frame_number(case["number"], *rate, case["start"], case["start_number"]) == case["timecode"]


@pytest.mark.parametrize("case", EXAMPLES["numbered_refused"], ids=lambda c: c["timecode"])
def test_frame_numbers_below_zero_are_refused(case):
    with pytest.raises(ValueError):
        tc.frame_number(case["timecode"], case["fps"], case["drop_frame"], case["start"], case["start_number"])


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
