from functools import lru_cache

import numpy as np
from moviepy import VideoFileClip  # MoviePy 2.x
from PIL import Image, ImageDraw, ImageFont

# ASCII characters from light to dense
ASCII_CHARS = " .'`:;irsXA253hMHGS#9B&@"

# Monospaced fonts to try, in order. Add your own path if none of these exist.
FONT_CANDIDATES = [
    "/System/Library/Fonts/Menlo.ttc",                       # macOS
    "C:/Windows/Fonts/consola.ttf",                          # Windows (Consolas)
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",   # Linux (DejaVu Sans Mono)
]


@lru_cache(maxsize=None)
def get_font(font_size):
    """
    Load the font and measure its character cell once per font size.
    Returns (font, cell_width_px, cell_height_px, top_offset_px).
    """
    font = None
    for path in FONT_CANDIDATES:
        try:
            font = ImageFont.truetype(path, font_size)
            break
        except OSError:
            continue

    if font is None:
        raise RuntimeError(
            "No monospaced font found. Add a font path to FONT_CANDIDATES."
        )

    bbox = font.getbbox("M")
    cell_width = round(font.getlength("M"))  # true horizontal step between characters
    cell_height = bbox[3] - bbox[1]          # height of a capital letter
    top_offset = bbox[1]                     # gap above the letter, used to align rows
    return font, cell_width, cell_height, top_offset


def pixel_to_ascii_char(gray_value):
    """
    Map a grayscale value (0-255) to a character in ASCII_CHARS.
    """
    scale = len(ASCII_CHARS)
    index = int(gray_value / 255 * (scale - 1))
    return ASCII_CHARS[index]


def frame_to_ascii_image(frame, target_char_width=80, font_size=14):
    """
    Convert a video frame (NumPy array, shape (h, w, 3), RGB)
    into a colored ASCII-art image (NumPy array).
    """
    original_h, original_w, _ = frame.shape
    aspect_ratio = original_w / original_h

    # Font is loaded and measured once, then cached
    font, char_width_px, char_height_px, top_offset = get_font(font_size)

    # Account for characters being taller than they are wide
    char_aspect = char_width_px / char_height_px
    target_char_height = max(1, int(target_char_width / aspect_ratio * char_aspect))

    # Shrink the frame to one pixel per character
    pil_frame = Image.fromarray(frame)
    pil_frame_small = pil_frame.resize(
        (target_char_width, target_char_height),
        Image.Resampling.LANCZOS,
    )

    # Output size, padded to even numbers (libx264 requires even dimensions)
    out_width = target_char_width * char_width_px
    out_height = target_char_height * char_height_px
    out_width += out_width % 2
    out_height += out_height % 2

    ascii_img = Image.new("RGB", (out_width, out_height), color=(0, 0, 0))
    draw = ImageDraw.Draw(ascii_img)

    small_pixels = np.array(pil_frame_small)

    for row in range(target_char_height):
        for col in range(target_char_width):
            r, g, b = small_pixels[row, col]

            # Perceived brightness
            gray = int(0.299 * r + 0.587 * g + 0.114 * b)
            ascii_char = pixel_to_ascii_char(gray)

            # Keep the original pixel color for the character
            text_color = (int(r), int(g), int(b))

            x_pos = col * char_width_px
            y_pos = row * char_height_px - top_offset

            draw.text((x_pos, y_pos), ascii_char, font=font, fill=text_color)

    return np.array(ascii_img)


def process_frame(frame):
    return frame_to_ascii_image(frame, target_char_width=80, font_size=14)


def main():
    input_video = "input.mp4"
    output_video = "ascii_output.mp4"

    clip = VideoFileClip(input_video)

    # MoviePy 2.x: image_transform() replaced fl_image()
    ascii_clip = clip.image_transform(process_frame)

    ascii_clip.write_videofile(
        output_video,
        codec="libx264",
        audio_codec="aac",
    )

    clip.close()
    ascii_clip.close()


if __name__ == "__main__":
    main()
