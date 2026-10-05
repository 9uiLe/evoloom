"""Exercise detail editing and simulated button transitions in the review host."""

import argparse
import json
import os
import time
from datetime import UTC, datetime
from pathlib import Path

from PIL import Image, ImageChops
from sim_use_session import (
    APP_ID,
    SimUseSession,
    install_existing_host,
    record_environment,
)
from tasks import ROOT, doctor, run_host

HOST_SAFE_AREA_TOP = 62
HOST_SAFE_AREA_BOTTOM = 34


def tap(review: SimUseSession, label: str, role: str = "Button") -> None:
    review.entry(review.ui(f"before-tap-{label}"), role, label)
    review.sim("tap", "--label", label, "--element-type", role)


def tap_text_area(review: SimUseSession, label: str) -> None:
    # The AX frame includes blank editor space. Aim inside the first text line.
    frame = review.entry(review.ui(f"before-tap-{label}"), "TextArea", label)["frame"]
    review.sim(
        "tap",
        "--point",
        f"{round(frame['x'] + 40)},{round(frame['y'] + 20)}",
    )


def require_keyboard(review: SimUseSession, visible: bool) -> None:
    if not review.keyboard(visible):
        raise AssertionError(f"Expected software keyboard visible={visible}")


def dismiss_keyboard_if_visible(review: SimUseSession) -> None:
    if review.sim("keyboard-state")["visible"]:
        review.sim("ios", "key", "41")
        require_keyboard(review, False)


def save_reachable(review: SimUseSession, data: dict, observation: str) -> bool:
    matches = [
        item
        for item in data["entries"]
        if item["role"] == "Button" and item.get("label") == "Save project"
    ]
    if not matches:
        return False
    if len(matches) != 1:
        raise AssertionError(f"Expected one Save project Button, found {len(matches)}")
    button = matches[0]
    if "disabled" in button["states"]:
        raise AssertionError("Save project is disabled")
    frame, screen = button["frame"], data["screen"]
    if frame["width"] < 44 or frame["height"] < 44:
        raise AssertionError(f"Save project has an undersized operation area: {frame}")
    # Measured from the key window on the pinned 402 × 874 pt iPhone 18 Pro.
    if (screen["width"], screen["height"]) != (402, 874):
        raise AssertionError(f"Unexpected review scene size: {screen}")
    if not (
        frame["x"] >= screen["x"]
        and frame["y"] >= screen["y"] + HOST_SAFE_AREA_TOP
        and frame["x"] + frame["width"] <= screen["x"] + screen["width"]
        and frame["y"] + frame["height"]
        <= screen["y"] + screen["height"] - HOST_SAFE_AREA_BOTTOM
    ):
        return False
    center = (
        round(frame["x"] + frame["width"] / 2),
        round(frame["y"] + frame["height"] / 2),
    )
    try:
        hit = review.sim("ui", "--point", f"{center[0]},{center[1]}")
    except RuntimeError as error:
        if "No translation object returned for simulator" in str(error):
            return False
        raise
    (review.directory / f"{review.prefix}-{observation}-hit.ui.json").write_text(
        json.dumps(hit, ensure_ascii=False, indent=2) + "\n"
    )
    return hit.get("appPackage") == APP_ID and any(
        item["role"] == "Button" and item.get("label") == "Save project"
        for item in hit["entries"]
    )


def outer_scroll(review: SimUseSession, data: dict) -> None:
    editor = review.entry(data, "TextArea", "Notes")["frame"]
    screen = data["screen"]
    editor_right = editor["x"] + editor["width"]
    screen_right = screen["x"] + screen["width"]
    if editor_right >= screen_right:
        raise AssertionError("No outer ScrollView gesture lane beside Notes")
    lane = round((editor_right + screen_right) / 2)
    # The fixed 402 × 874 pt scene previously used 390,500 → 390,220.
    review.sim(
        "swipe",
        "--from",
        f"{lane},{round(screen['height'] * 0.57)}",
        "--to",
        f"{lane},{round(screen['height'] * 0.25)}",
        "--coordinate-space",
        "ui",
    )


def reach_save(review: SimUseSession, initial: dict, observation: str) -> dict:
    current = initial
    for attempt in range(3):
        if save_reachable(review, current, f"{observation}-{attempt}"):
            return current
        if attempt < 2:
            outer_scroll(review, current)
            current = review.ui(f"{observation}-after-outer-scroll-{attempt + 1}")
    raise AssertionError(
        "Save project remained outside the screen or obscured after two outer swipes"
    )


def require_editor_content_moved(
    review: SimUseSession, frame: dict, screen: dict
) -> None:
    before_path = review.directory / "detail-editor-before-internal-scroll.png"
    after_path = review.directory / "detail-editor-internal-scroll.png"
    with Image.open(before_path) as before_image, Image.open(after_path) as after_image:
        if before_image.size != after_image.size:
            raise AssertionError("Editor screenshots have different dimensions")
        scale = before_image.width / screen["width"]
        bounds = (
            round((frame["x"] + 2) * scale),
            round((frame["y"] + 2) * scale),
            round((frame["x"] + frame["width"] - 2) * scale),
            round((frame["y"] + frame["height"] - 2) * scale),
        )
        before = before_image.convert("RGB").crop(bounds)
        after = after_image.convert("RGB").crop(bounds)
        changed = ImageChops.difference(before, after).convert("L").histogram()
    if sum(changed[21:]) < 1_000:
        raise AssertionError("Editor swipe did not visibly move its text")


def large_detail(review: SimUseSession) -> None:
    original_size = review.command(
        "xcrun", "simctl", "ui", review.device, "content_size"
    )
    try:
        review.command(
            "xcrun",
            "simctl",
            "ui",
            review.device,
            "content_size",
            "accessibility-medium",
        )
        if (
            review.command("xcrun", "simctl", "ui", review.device, "content_size")
            != "accessibility-medium"
        ):
            raise AssertionError("Simulator did not adopt accessibility-medium")
        large = review.launch("detail")
        review.entry(large, "TextArea", "Notes")
        review.screenshot("large-before-edit")
        tap_text_area(review, "Notes")
        require_keyboard(review, True)
        review.screenshot("large-notes-keyboard")
        before = review.ui("large-before-outer-scroll")
        if not save_reachable(review, before, "large-with-keyboard"):
            outer_scroll(review, before)
            review.ui("large-after-outer-scroll")
            review.screenshot("large-scrolled-keyboard")
        dismiss_keyboard_if_visible(review)
        reach_save(review, review.ui("large-after-keyboard-dismissal"), "large-save")
        review.screenshot("large-save-reached")
    finally:
        review.command(
            "xcrun", "simctl", "ui", review.device, "content_size", original_size
        )


def detail(review: SimUseSession) -> None:
    review.prefix = "detail"
    large_detail(review)
    review.launch("detail")
    initial = review.ui("detail-initial")
    review.entry(initial, "Heading", "Project details")
    reach_save(review, initial, "initial-save")
    review.screenshot("light-save-reached")
    original_title = review.entry(initial, "TextField", "Title")["value"]
    original_notes = review.entry(initial, "TextArea", "Notes")["value"]
    review.screenshot("light-before-edit")

    tap(review, "Title", "TextField")
    review.sim("keyboard-state")
    review.screenshot("title-focused")
    tap_text_area(review, "Notes")
    review.sim("keyboard-state")
    review.screenshot("notes-focused")
    review.sim("type", " Added research findings.")
    review.await_ui(
        "notes-first-edit",
        lambda data: (
            len(review.entry(data, "TextArea", "Notes").get("value", ""))
            > len(original_notes) + 10
        ),
    )
    review.sim("ios", "key", "40")
    multiline_notes = review.await_ui(
        "notes-newline",
        lambda data: "\n" in review.entry(data, "TextArea", "Notes").get("value", ""),
    )
    review.sim("type", "Next action is review.")
    notes = review.await_ui(
        "notes-multiline-edit",
        lambda data: (
            len(review.entry(data, "TextArea", "Notes").get("value", ""))
            > len(review.entry(multiline_notes, "TextArea", "Notes")["value"]) + 10
        ),
    )
    if (
        original_notes == review.entry(notes, "TextArea", "Notes").get("value")
        or "\n" not in review.entry(notes, "TextArea", "Notes")["value"]
    ):
        raise AssertionError("Notes did not change after multiline editing")
    review.screenshot("notes-edited")

    # Fixed long content tests the editor's own scroll without slow bulk typing.
    before_inner = review.launch("detailLongNotes")
    if len(review.entry(before_inner, "TextArea", "Notes")["value"]) <= 500:
        raise AssertionError("Long Notes fixture did not load")
    review.screenshot("editor-before-internal-scroll")
    editor = review.entry(before_inner, "TextArea", "Notes")["frame"]
    review.sim(
        "swipe",
        "--from",
        f"{round(editor['x'] + editor['width'] / 2)},{round(editor['y'] + editor['height'] - 20)}",
        "--to",
        f"{round(editor['x'] + editor['width'] / 2)},{round(editor['y'] + 20)}",
        "--coordinate-space",
        "ui",
    )
    after_inner = review.ui("after-editor-scroll")
    before_editor_y = review.entry(before_inner, "TextArea", "Notes")["frame"]["y"]
    after_editor_y = review.entry(after_inner, "TextArea", "Notes")["frame"]["y"]
    if abs(after_editor_y - before_editor_y) > 3:
        raise AssertionError(
            "Editor swipe moved the outer ScrollView instead of editor content"
        )
    review.screenshot("editor-internal-scroll")
    require_editor_content_moved(review, editor, before_inner["screen"])

    reach_save(review, review.ui("save-reached"), "save-after-editor-scroll")
    review.screenshot("save-reached")

    review.launch("detail")
    tap(review, "Title", "TextField")
    review.sim("type", "X")
    edited = review.await_ui(
        "title-edited",
        lambda data: (
            review.entry(data, "TextField", "Title").get("value", "") != original_title
            and review.entry(data, "TextField", "Title").get("value", "").endswith("X")
        ),
    )
    review.entry(edited, "Heading", "Project details")
    review.screenshot("title-edited")

    japanese = review.launch("detailJapanese")
    review.entry(japanese, "Heading", "プロジェクトの詳細")
    review.entry(japanese, "TextField", "タイトル")
    review.entry(japanese, "TextArea", "メモ")
    review.entry(japanese, "Button", "プロジェクトを保存")
    review.screenshot("japanese-long")

    dark = review.launch("detail", "dark")
    review.entry(dark, "TextArea", "Notes")
    review.screenshot("dark-before-edit")
    tap_text_area(review, "Notes")
    review.screenshot("dark-notes-focused")
    dismiss_keyboard_if_visible(review)


def button_state(
    review: SimUseSession, status: str, count: int, action: str, disabled: bool
) -> dict:
    data = review.await_ui(
        f"button-{status}-{count}",
        lambda current: (
            any(item.get("label") == status for item in current["entries"])
            and any(
                item.get("label") == f"Runs started: {count}"
                for item in current["entries"]
            )
        ),
    )
    button = review.entry(data, "Button", action)
    if ("disabled" in button["states"]) != disabled:
        raise AssertionError(
            f"{action}: expected disabled={disabled}, got {button['states']}"
        )
    return data


def tap_disabled_button(
    review: SimUseSession, data: dict, label: str, count: int
) -> None:
    frame = review.entry(data, "Button", label)["frame"]
    review.sim(
        "tap",
        "--point",
        f"{round(frame['x'] + frame['width'] / 2)},{round(frame['y'] + frame['height'] / 2)}",
    )
    unchanged = review.ui("after-disabled-tap")
    review.entry(unchanged, "StaticText", f"Runs started: {count}")


def button_flow(review: SimUseSession) -> None:
    review.prefix = "button"
    review.ui("button-initial")
    ready = button_state(review, "Ready", 0, "Run review", False)
    review.entry(ready, "CheckBox", "Disable action from parent")
    review.screenshot("ready-light")
    tap(review, "Run review")
    running = button_state(review, "Processing", 1, "Run review", True)
    review.screenshot("running-light")
    tap_disabled_button(review, running, "Run review", 1)
    tap(review, "Finish with error")
    button_state(review, "Failed", 1, "Try again", False)
    review.screenshot("failed-light")
    tap(review, "Try again")
    running_again = button_state(review, "Processing", 2, "Run review", True)
    tap_disabled_button(review, running_again, "Run review", 2)
    tap(review, "Complete successfully")
    completed = button_state(review, "Completed", 2, "Run again", False)
    review.screenshot("completed-light")

    toggle = review.entry(completed, "CheckBox", "Disable action from parent")["frame"]
    review.sim(
        "tap",
        "--point",
        f"{round(toggle['x'] + toggle['width'] - 35)},{round(toggle['y'] + toggle['height'] / 2)}",
        "--duration",
        "0.05",
    )
    disabled = review.await_ui(
        "externally-disabled",
        lambda data: (
            review.entry(data, "CheckBox", "Disable action from parent").get("value")
            == "1"
        ),
    )
    if "disabled" not in review.entry(disabled, "Button", "Run again")["states"]:
        raise AssertionError(
            "Parent disabled state was not applied to the native Button"
        )
    tap_disabled_button(review, disabled, "Run again", 2)
    review.screenshot("externally-disabled")

    review.launch("buttonFlow", "dark")
    button_state(review, "Ready", 0, "Run review", False)
    tap(review, "Run review")
    button_state(review, "Processing", 1, "Run review", True)
    review.screenshot("running-dark")
    tap(review, "Finish with error")
    button_state(review, "Failed", 1, "Try again", False)
    review.screenshot("failed-dark")

    original_size = review.command(
        "xcrun", "simctl", "ui", review.device, "content_size"
    )
    try:
        review.command(
            "xcrun",
            "simctl",
            "ui",
            review.device,
            "content_size",
            "accessibility-medium",
        )
        japanese = review.launch("buttonFlowJapanese")
        review.entry(japanese, "Button", "確認を実行する")
        review.screenshot("japanese-large-ready")
        tap(review, "確認を実行する")
        large_running = review.await_ui(
            "japanese-large-running",
            lambda data: any(item.get("label") == "処理中" for item in data["entries"]),
        )
        if (
            "disabled"
            not in review.entry(large_running, "Button", "確認を実行する")["states"]
        ):
            raise AssertionError("Japanese large-text loading Button is not disabled")
        review.screenshot("japanese-large-running")
    finally:
        review.command(
            "xcrun", "simctl", "ui", review.device, "content_size", original_size
        )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=["detail", "button"], required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--reuse-built-host", action="store_true")
    args = parser.parse_args()
    device = doctor()
    directory = args.output or ROOT / "TestResults/SimUse" / datetime.now(UTC).strftime(
        f"%Y%m%dT%H%M%SZ-{args.scenario}"
    )
    review = SimUseSession(device, directory)
    os.environ.update(
        EVOLOOM_SCREEN="detail" if args.scenario == "detail" else "buttonFlow",
        EVOLOOM_STATE="normal",
        EVOLOOM_APPEARANCE="light",
    )
    started = time.monotonic()
    try:
        if args.reuse_built_host:
            install_existing_host(review)
        else:
            run_host()
        review.launch("detail" if args.scenario == "detail" else "buttonFlow")
        record_environment(directory, device)
        if args.scenario == "detail":
            detail(review)
        else:
            button_flow(review)
    except Exception as error:
        (directory / "failure.txt").write_text(f"{type(error).__name__}: {error}\n")
        print(
            f"{args.scenario}: failed after {time.monotonic() - started:.1f}s; evidence: {directory}"
        )
        raise
    print(
        f"{args.scenario}: passed in {time.monotonic() - started:.1f}s; evidence: {directory}"
    )


if __name__ == "__main__":
    main()
