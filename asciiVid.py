import numpy as np
from moviepy import VideoFileClip
from PIL import Image, ImageDraw, ImageFont

# ASCII characters from light to dark
ASCII_CHARS = " .'`:;irsXA253hMHGS#9B&@"

# !!!! macOS monospaced font (change if on Windows) !!!!
FONT_PATH = "/System/Library/Fonts/Menlo.ttc"


def pixel_to_ascii_char(gray_value):
    """
    Map a grayscale value (0-255) to a character in ASCII_CHARS.
    """
    scale = len(ASCII_CHARS)
    index = int(gray_value / 255 * (scale - 1))
    return ASCII_CHARS[index]


def frame_to_ascii_image(frame, target_char_width=80, font_size=14):
    """
    Convert a video frame into a colored ASCII-art image.
    """

    # Original frame dimensions
    original_h, original_w, _ = frame.shape
    aspect_ratio = original_w / original_h

    # Load monospaced font
    try:
        font = ImageFont.truetype(FONT_PATH, font_size)
    except OSError:
        print("Warning: Menlo not found. Using Pillow default font.")
        font = ImageFont.load_default()

    # Measure actual character dimensions
    bbox = font.getbbox("M")
    char_width_px = bbox[2] - bbox[0]
    char_height_px = bbox[3] - bbox[1]

    # Account for the physical aspect ratio of the characters
    char_aspect = char_width_px / char_height_px

    target_char_height = int(
        target_char_width / aspect_ratio * char_aspect
    )

    target_char_height = max(1, target_char_height)

    # Convert frame to PIL and shrink it to ASCII resolution
    pil_frame = Image.fromarray(frame)

    pil_frame_small = pil_frame.resize(
        (target_char_width, target_char_height),
        Image.Resampling.LANCZOS
    )

    # Final output dimensions
    out_width = target_char_width * char_width_px
    out_height = target_char_height * char_height_px

    ascii_img = Image.new(
        "RGB",
        (out_width, out_height),
        color=(0, 0, 0)
    )

    draw = ImageDraw.Draw(ascii_img)

    # Pixel data from downscaled frame
    small_pixels = np.array(pil_frame_small)

    for row in range(target_char_height):
        for col in range(target_char_width):

            r, g, b = small_pixels[row, col]

            # Convert RGB to perceived brightness
            gray = int(
                0.299 * r +
                0.587 * g +
                0.114 * b
            )

            ascii_char = pixel_to_ascii_char(gray)

            # Preserve original pixel color
            text_color = (
                int(r),
                int(g),
                int(b)
            )

            x_pos = col * char_width_px
            y_pos = row * char_height_px - bbox[1]

            draw.text(
                (x_pos, y_pos),
                ascii_char,
                font=font,
                fill=text_color
            )

    return np.array(ascii_img)


def process_frame(frame):
    return frame_to_ascii_image(
        frame,
        target_char_width=80,
        font_size=14
    )


def main():

    input_video = "input.mp4"
    output_video = "ascii_output.mp4"

    # MoviePy 2.x
    clip = VideoFileClip(input_video)

    # fl_image() was replaced by image_transform()
    ascii_clip = clip.image_transform(process_frame)

    ascii_clip.write_videofile(
        output_video,
        codec="libx264",
        audio_codec="aac"
    )

    clip.close()
    ascii_clip.close()


if __name__ == "__main__":
    main()
