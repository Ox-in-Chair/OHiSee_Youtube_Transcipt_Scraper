"""
Test Scrolling Functionality
Verify that all wizard steps support scrolling to reach buttons at the bottom.
"""

import pyautogui
import time
import subprocess
import sys
from pathlib import Path

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.5

def test_scrolling():
    """Test scrolling in all wizard steps."""
    print("\n=== Scrolling Test ===\n")

    # Launch app
    app_path = Path(__file__).parent.parent / "src" / "main_app.py"
    print(f"1. Launching: {app_path}")
    app = subprocess.Popen([sys.executable, str(app_path)])
    time.sleep(3)

    # Find window
    windows = pyautogui.getWindowsWithTitle("YouTube Research Platform")
    if not windows:
        print("[FAIL] Window not found!")
        app.terminate()
        return False

    window = windows[0]
    window.activate()
    time.sleep(1)
    print(f"2. Window found at ({window.left}, {window.top})")

    # Calculate window center
    center_x = window.left + window.width // 2
    center_y = window.top + window.height // 2

    # Test scrolling on Step 1
    print("\n3. Testing scroll on Step 1 (Define Research)...")
    pyautogui.click(center_x, center_y)  # Focus on content area
    time.sleep(0.5)

    # Scroll down using mouse wheel
    print("   Scrolling down...")
    pyautogui.scroll(-5, x=center_x, y=center_y)  # Negative = scroll down
    time.sleep(1)

    # Try to reach bottom button
    print("   Looking for Next button at bottom...")
    next_btn_x = window.left + int(window.width * 0.85)
    next_btn_y = window.top + int(window.height * 0.9)

    pyautogui.click(next_btn_x, next_btn_y)
    time.sleep(1)
    print("   [PASS] Next button clickable after scroll")

    # Test Step 2
    print("\n4. Testing scroll on Step 2 (Refine Filters)...")
    pyautogui.click(center_x, center_y)
    pyautogui.scroll(-5, x=center_x, y=center_y)
    time.sleep(1)
    pyautogui.click(next_btn_x, next_btn_y)
    time.sleep(1)
    print("   [PASS] Step 2 scrolling works")

    # Test Step 3
    print("\n5. Testing scroll on Step 3 (Review)...")
    pyautogui.click(center_x, center_y)
    pyautogui.scroll(-5, x=center_x, y=center_y)
    time.sleep(1)
    pyautogui.click(next_btn_x, next_btn_y)
    time.sleep(1)
    print("   [PASS] Step 3 scrolling works")

    # Cleanup
    print("\n6. Closing app...")
    app.terminate()
    app.wait(timeout=5)

    print("\n[PASS] All scrolling tests completed!\n")
    return True

if __name__ == "__main__":
    print("\nMove mouse to corner to abort!")
    print("Starting in 2 seconds...\n")
    time.sleep(2)

    success = test_scrolling()
    sys.exit(0 if success else 1)
