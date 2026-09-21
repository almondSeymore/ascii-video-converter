
# ASCII Video Converter

Converts a video into a color ASCII-art version of itself. Each frame is
shrunk to a grid of characters, each cell's brightness picks a character
from a density ramp, and the character is drawn in the original pixel's color.

## How it works

1. Read each frame with MoviePy as a NumPy array
2. Resize the frame to a small character grid with Pillow, adjusting for
   characters being taller than they are wide
3. Convert each cell to grayscale and map it to one of 24 characters,
   from light (`.`) to dense (`@`)
4. Draw each character in the source pixel's color on a black background
5. Re-encode the frames into a new video with MoviePy (libx264)

## Usage

```bash
pip install moviepy pillow numpy
python [asciiVid].py
```

Put your video at `input.mp4`. The result is saved as `ascii_output.mp4`.

## Settings

- `target_char_width`: number of characters across (default 80). Higher means more detail and slower rendering.
- `font_size`: size of the drawn characters (default 14)

## Notes

- Tested with MoviePy [version]. MoviePy 2.x renamed some functions, so pin the version in `requirements.txt` if you update.
- [Add a rendering-time note or improvement here once you've measured it.]
