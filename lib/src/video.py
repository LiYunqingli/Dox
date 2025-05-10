import os
import cv2
import time
import signal
import numpy as np
from PIL import Image

# 全局变量用于信号处理
exit_flag = False

def signal_handler(sig, frame):
    global exit_flag
    exit_flag = True

def video_in_cmd(video_path):
    global exit_flag
    original_signal = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, signal_handler)
    exit_flag = False  # 重置标志
    
    try:
        try:
            cols, rows = os.get_terminal_size()
            rows -= 1
        except:
            cols, rows = 80, 24
        
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError("无法打开视频文件")
        
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_delay = 1 / fps if fps != 0 else 0.1
        video_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        video_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        aspect_ratio = video_width / video_height if video_height != 0 else 1
        
        target_height = rows * 2
        target_width = int(target_height * aspect_ratio)
        if target_width > cols:
            target_width = cols
            target_height = int(target_width / aspect_ratio)
        
        target_height = max((target_height // 2) * 2, 2)
        target_height = min(target_height, rows * 2)
        target_width = int(target_height * aspect_ratio)
        target_width = min(target_width, cols)
        
        try:
            while cap.isOpened() and not exit_flag:
                start_time = time.perf_counter()
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(frame).resize((target_width, target_height))
                pixels = img.load()
                
                output = []
                for y in range(0, target_height, 2):
                    line = []
                    for x in range(target_width):
                        upper = pixels[x, y]
                        lower = pixels[x, y+1] if y+1 < target_height else (0, 0, 0)
                        line.append(
                            f"\033[38;2;{upper[0]};{upper[1]};{upper[2]}m"
                            f"\033[48;2;{lower[0]};{lower[1]};{lower[2]}m▀"
                        )
                    output.append("".join(line) + "\033[0m")
                
                while len(output) < rows:
                    output.append("\033[0m")
                
                print(f"\033[H{chr(27)}[?25l", end='')
                print("\n".join(output))
                
                elapsed = time.perf_counter() - start_time
                remaining_time = frame_delay - elapsed - 0.001
                time.sleep(max(0, remaining_time))
        
        finally:
            cap.release()
            print(f"{chr(27)}[?25h")
    
    except Exception as e:
        print(f"Error: {e}")
        input()
    
    finally:
        signal.signal(signal.SIGINT, original_signal)