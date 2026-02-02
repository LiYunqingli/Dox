import os
import signal
import time
from typing import Optional

from PIL import Image


def _enable_virtual_terminal_processing() -> None:
    """在Windows终端上启用ANSI转义序列处理。"""
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
        return


# 全局变量用于信号处理
exit_flag = False


def _signal_handler(sig, frame):
    global exit_flag
    exit_flag = True


def _get_terminal_size() -> tuple[int, int]:
    try:
        cols, rows = os.get_terminal_size()
        rows = max(rows - 1, 1)
        return cols, rows
    except Exception:
        return 80, 24


def video_in_cmd(
    video_path: str,
    *,
    max_width: Optional[int] = None,
    max_height: Optional[int] = None,
    fps: Optional[float] = None,
    loop: bool = False,
    grayscale: bool = False,
    no_color: bool = False,
    page_break: bool = True,
) -> None:
    """在终端中播放视频。

    渲染策略：
    - 默认：使用半块字符 (▀) 的24位彩色块
    - grayscale：保持块状但将颜色转换为灰度
    - no_color：无ANSI颜色的ASCII梯度（更兼容）
    """

    global exit_flag

    _enable_virtual_terminal_processing()

    try:
        import cv2
    except Exception as e:
        raise ImportError("缺少依赖：opencv-python (cv2)，无法播放视频") from e

    original_signal = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, _signal_handler)
    exit_flag = False

    term_cols, term_rows = _get_terminal_size()
    cols, rows = term_cols, term_rows
    if max_width is not None:
        cols = max(1, int(max_width))
    if max_height is not None:
        rows = max(1, int(max_height))

    def luma(rgb: tuple[int, int, int]) -> int:
        return int(0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2])

    cap = None
    cursor_hidden = False
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("无法打开视频文件")

        # 翻页：避免后续使用 \033[H 回到左上角重绘时覆盖之前的命令输出。
        # 不使用 clear/cls，这样历史输出仍可在滚动区查看。
        if page_break:
            print("\n" * max(term_rows, 1), end="", flush=True)
            print("\033[H", end="", flush=True)

        src_fps = float(cap.get(cv2.CAP_PROP_FPS) or 0.0)
        use_fps = float(fps) if fps is not None else src_fps
        if use_fps <= 0:
            use_fps = 10.0
        frame_delay = 1.0 / use_fps

        video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
        video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
        aspect_ratio = (video_width / video_height) if video_height else 1.0

        target_height = rows * 2
        target_width = int(target_height * aspect_ratio) if aspect_ratio else cols
        if target_width > cols:
            target_width = cols
            target_height = int(target_width / aspect_ratio) if aspect_ratio else target_height

        target_height = max((target_height // 2) * 2, 2)
        target_height = min(target_height, rows * 2)
        target_width = max(1, min(int(target_height * aspect_ratio) if aspect_ratio else cols, cols))

        # Hide cursor once
        print(f"{chr(27)}[?25l", end="")
        cursor_hidden = True

        while cap.isOpened() and not exit_flag:
            start_time = time.perf_counter()
            ret, frame = cap.read()
            if not ret:
                if loop:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                break

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame).resize((target_width, target_height), Image.BILINEAR)

            if no_color:
                img = img.convert("L")
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

                while len(output_lines) < rows:
                    output_lines.append("")

                print("\033[H", end="")
                print("\n".join(output_lines))
            else:
                img = img.convert("RGB")
                pixels = img.load()
                output_lines = []
                for y in range(0, target_height, 2):
                    parts = []
                    for x in range(target_width):
                        upper = pixels[x, y]
                        lower = pixels[x, y + 1] if y + 1 < target_height else (0, 0, 0)

                        if grayscale:
                            u = luma(upper)
                            l = luma(lower)
                            upper = (u, u, u)
                            lower = (l, l, l)

                        parts.append(
                            f"\033[38;2;{upper[0]};{upper[1]};{upper[2]}m"
                            f"\033[48;2;{lower[0]};{lower[1]};{lower[2]}m▀"
                        )
                    output_lines.append("".join(parts) + "\033[0m")

                while len(output_lines) < rows:
                    output_lines.append("\033[0m")

                print("\033[H", end="")
                print("\n".join(output_lines))

            elapsed = time.perf_counter() - start_time
            remaining_time = frame_delay - elapsed
            if remaining_time > 0:
                time.sleep(remaining_time)

    finally:
        try:
            if cap is not None:
                cap.release()
        finally:
            if cursor_hidden:
                print(f"{chr(27)}[?25h", end="")
            signal.signal(signal.SIGINT, original_signal)