# Lightning-Trim
Command-Line or GUI program to precisely trim a video file as fast as possible, while still re-encoding first keyframe to align timestamp. The rest of the video is not re-encoded, which vastly saves rendering time, at the cost of inability to adjust compression.

## Usage
The GUI can be accessed through running the program without any arguments (requires Python, EasyGUI and FFmpeg), or by running the appropriate build directly.
Alternatively, both implementations offer a command-line interface which is invoked as follows:
- `lightning <input-file> <start> <end> <output-file>?`
  - where `lightning` is `python3 lightning.py`, `py lightning.py`, `lightning.exe`, etc depending on platform
  - and `output-file` is optional (defaults to `input-file` with "~t" appended before extension).

## Additional notes
- Dependencies are included in the build branch.
- Does *not* function on raw image or audio files (possibly future update if there is demand).
- The first keyframe of the video starting from the seek position is re-encoded with CRF (Constant Rate Factor) of 20. This is currently set as a balance for higher quality at the beginning, and cannot be changed.
