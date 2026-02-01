import os
from typing import Optional

from PIL import Image


def _enable_virtual_terminal_processing() -> None:
    """Enable ANSI escape sequence processing on Windows terminals."""
    if os.name != "nt":
        return

    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)) == 0:
            return

        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        new_mode = mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING
        kernel32.SetConsoleMode(handle, new_mode)
    except Exception:
        # Best-effort; if it fails, output may still work on modern terminals.
        return


def image_in_cmd(
    image_path: str,
    *,
    max_width: Optional[int] = None,
    max_height: Optional[int] = None,
    grayscale: bool = False,
    no_color: bool = False,
) -> None:
    """Render an image to the terminal using low-resolution blocks.

    Uses a half-block character (▀) so each terminal row represents two pixel rows.
    """

    _enable_virtual_terminal_processing()

    try:
        cols, rows = os.get_terminal_size()
        rows = max(rows - 1, 1)
    except Exception:
        cols, rows = 80, 24

    if max_width is not None:
        cols = max(1, int(max_width))
    if max_height is not None:
        rows = max(1, int(max_height))

    img = Image.open(image_path)

    if no_color:
        img = img.convert("L")
    else:
        img = img.convert("RGB")

    src_width, src_height = img.size
    if src_height == 0:
        raise ValueError("Invalid image height")

    aspect_ratio = src_width / src_height

    target_height = rows * 2
    target_width = int(target_height * aspect_ratio)

    if target_width > cols:
        target_width = cols
        target_height = int(target_width / aspect_ratio) if aspect_ratio != 0 else target_height

    # Ensure an even pixel height (paired rows for ▀)
    target_height = max((target_height // 2) * 2, 2)
    target_height = min(target_height, rows * 2)
    target_width = max(1, min(int(target_height * aspect_ratio), cols))

    img = img.resize((target_width, target_height), Image.BILINEAR)

    if no_color:
        pixels = img.load()
        ramp = " .:-=+*#%@"
        ramp_len = len(ramp) - 1
        output_lines = []
        for y in range(0, target_height, 2):
            line_chars = []
            for x in range(target_width):
                upper = pixels[x, y]
                lower = pixels[x, y + 1] if y + 1 < target_height else 0
                v = (int(upper) + int(lower)) // 2
                ch = ramp[int(v / 255 * ramp_len)]
                line_chars.append(ch)
            output_lines.append("".join(line_chars))

        print("\n".join(output_lines))
        return

    pixels = img.load()
    output_lines = []
    for y in range(0, target_height, 2):
        parts = []
        for x in range(target_width):
            upper = pixels[x, y]
            lower = pixels[x, y + 1] if y + 1 < target_height else (0, 0, 0)

            if grayscale:
                def luma(rgb):
                    return int(0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2])

                u = luma(upper)
                l = luma(lower)
                upper = (u, u, u)
                lower = (l, l, l)

            parts.append(
                f"\033[38;2;{upper[0]};{upper[1]};{upper[2]}m"
                f"\033[48;2;{lower[0]};{lower[1]};{lower[2]}m▀"
            )
        output_lines.append("".join(parts) + "\033[0m")

    print("\n".join(output_lines))
