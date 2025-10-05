"""
Quick GUI Test - YouTube Research Platform
Minimal smoke test using PyAutoGUI
"""

import pyautogui
import time
import subprocess
import sys
from pathlib import Path

# Safety settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.8

def quick_test():
    """Quick smoke test of the GUI."""
    print("\n=== Quick GUI Smoke Test ===\n")

    # Launch app
    app_path = Path(__file__).parent.parent / "src" / "main_app.py"
    print(f"1. Launching: {app_path}")
    app = subprocess.Popen([sys.executable, str(app_path)])
    time.sleep(3)

    # Get screen info
    screen_width, screen_height = pyautogui.size()
    print(f"2. Screen: {screen_width}x{screen_height}")

    # Find window
    windows = pyautogui.getWindowsWithTitle("YouTube Research Platform")
    if not windows:
        print("[FAIL] Window not found!")
        app.terminate()
        return False

    window = windows[0]
    window.activate()
    time.sleep(1)
    print(f"3. Window found at ({window.left}, {window.top})")

    # Quick interaction test
    center_x = window.left + window.width // 2
    center_y = window.top + window.height // 2

    print("4. Testing click at center...")
    pyautogui.click(center_x, center_y)
    time.sleep(1)

    print("5. Testing keyboard shortcut (F1)...")
    pyautogui.press("f1")
    time.sleep(1)

    print("6. Taking screenshot...")
    screenshot = pyautogui.screenshot()
    screenshot.save(Path(__file__).parent / "screenshot_test.png")
    print("   Saved: tests/screenshot_test.png")

    # Cleanup
    print("7. Closing app...")
    app.terminate()
    app.wait(timeout=5)

    print("\n[PASS] Quick test completed!\n")
    return True

if __name__ == "__main__":
    print("\nMove mouse to corner to abort!")
    print("Starting in 2 seconds...\n")
    time.sleep(2)

    success = quick_test()
    sys.exit(0 if success else 1)
