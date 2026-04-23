#!/usr/bin/env python3
"""Generate a 15-second city timelapse video (dawn to dusk) using the Runway ML API.

Usage:
    export RUNWAYML_API_SECRET="your_api_key"
    python generate_timelapse.py [--output city_timelapse.mp4]

The script first tries to generate the full 15 seconds in one shot using the
seedance2 model. If that fails (e.g. duration not supported), it falls back to
generating two gen4.5 clips (10s + 5s) and concatenating them with ffmpeg.
"""

import argparse
import os
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

from runwayml import RunwayML
from runwayml.lib.polling import TaskFailedError, TaskTimeoutError

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

_PROMPT_FULL = (
    "Cinematic timelapse of a busy city street transitioning from dawn to dusk. "
    "The sky shifts from soft pink and orange sunrise hues through clear bright blue midday sky "
    "to warm golden hour light and finally deep purple twilight. Street lamps flicker on as "
    "darkness descends. Cars and pedestrians flow in smooth time-lapse motion. "
    "High quality, wide-angle, photorealistic footage."
)

_PROMPT_DAWN_TO_NOON = (
    "Cinematic timelapse of a busy city street from dawn to midday. "
    "Sky transitions from soft pink and orange sunrise glow to bright blue sky with wispy clouds. "
    "Morning traffic and pedestrians fill the streets. Sharp, detailed, photorealistic footage."
)

_PROMPT_NOON_TO_DUSK = (
    "Cinematic timelapse of a busy city street from noon to dusk. "
    "Sky shifts from bright blue through warm golden-hour light to deep orange and purple twilight. "
    "Street lamps flicker on as the city transitions into evening. "
    "Photorealistic, wide-angle, continuous with earlier daytime footage."
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _download(url: str, dest: str) -> None:
    print(f"  Downloading → {dest}")
    urllib.request.urlretrieve(url, dest)


def _concat_with_ffmpeg(clips: list[str], output: str) -> None:
    """Concatenate MP4 clips using ffmpeg's concat demuxer."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as fh:
        for clip in clips:
            fh.write(f"file '{os.path.abspath(clip)}'\n")
        list_file = fh.name

    try:
        subprocess.run(
            [
                "ffmpeg", "-y",
                "-f", "concat", "-safe", "0", "-i", list_file,
                "-c", "copy",
                output,
            ],
            check=True,
            capture_output=True,
        )
    finally:
        os.unlink(list_file)


# ---------------------------------------------------------------------------
# Generation strategies
# ---------------------------------------------------------------------------

def _try_single_clip(client: RunwayML, output: str) -> bool:
    """Attempt one 15-second generation via seedance2. Returns True on success."""
    print("[Strategy 1] Submitting 15-second seedance2 task...")
    try:
        task = client.text_to_video.create(
            model="seedance2",
            prompt_text=_PROMPT_FULL,
            duration=15,
            ratio="1280:720",
        )
        print(f"  Task ID: {task.id}")
        print("  Waiting for completion (this can take several minutes)...")
        result = task.wait_for_task_output(timeout=900)

        if result.status == "SUCCEEDED" and result.output:
            _download(result.output[0], output)
            return True

        print(f"  Unexpected status: {result.status}")
        return False

    except TaskFailedError as exc:
        print(f"  Task failed: {exc.task_details}")
    except TaskTimeoutError:
        print("  Task timed out after 15 minutes.")
    except Exception as exc:  # noqa: BLE001
        print(f"  Error: {exc}")

    return False


def _generate_multi_clip(client: RunwayML, output: str) -> None:
    """Generate two gen4.5 clips (10s + 5s) concurrently, then concatenate."""
    print("[Strategy 2] Submitting two gen4.5 tasks concurrently (10s + 5s)...")

    task1 = client.text_to_video.create(
        model="gen4.5",
        prompt_text=_PROMPT_DAWN_TO_NOON,
        duration=10,
        ratio="1280:720",
    )
    print(f"  Clip 1 task ID: {task1.id}  (dawn → noon, 10s)")

    task2 = client.text_to_video.create(
        model="gen4.5",
        prompt_text=_PROMPT_NOON_TO_DUSK,
        duration=5,
        ratio="1280:720",
    )
    print(f"  Clip 2 task ID: {task2.id}  (noon → dusk, 5s)")

    with tempfile.TemporaryDirectory() as tmpdir:
        clip1 = os.path.join(tmpdir, "clip1.mp4")
        clip2 = os.path.join(tmpdir, "clip2.mp4")

        print("  Waiting for clip 1 (10s)...")
        result1 = task1.wait_for_task_output(timeout=900)
        _download(result1.output[0], clip1)

        print("  Waiting for clip 2 (5s)...")
        result2 = task2.wait_for_task_output(timeout=900)
        _download(result2.output[0], clip2)

        print("  Concatenating clips with ffmpeg...")
        _concat_with_ffmpeg([clip1, clip2], output)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--output", default="city_timelapse.mp4", help="Output MP4 path (default: city_timelapse.mp4)")
    args = parser.parse_args()

    api_key = os.environ.get("RUNWAYML_API_SECRET")
    if not api_key:
        sys.exit("Error: RUNWAYML_API_SECRET environment variable is not set.")

    client = RunwayML(api_key=api_key)
    output = args.output

    print(f"Generating 15-second city timelapse → {output}\n")

    if not _try_single_clip(client, output):
        print("\nFalling back to two-clip strategy...\n")
        _generate_multi_clip(client, output)

    size_mb = Path(output).stat().st_size / 1_000_000
    print(f"\nDone! Saved to {output} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    main()
