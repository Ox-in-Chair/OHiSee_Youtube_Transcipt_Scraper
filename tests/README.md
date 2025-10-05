# GUI Automation Tests

Automated testing suite for YouTube Research Platform using **PyAutoGUI MCP Server**.

## Overview

This directory contains automated GUI tests for the Tkinter-based YouTube Research Platform. Tests use PyAutoGUI to simulate mouse clicks, keyboard input, and verify UI behavior.

## Test Files

### 1. `quick_gui_test.py` - Quick Smoke Test
**Purpose**: Fast validation that GUI launches and responds
**Runtime**: ~10 seconds

```bash
python tests/quick_gui_test.py
```

**What it tests**:
- ✅ Application launches successfully
- ✅ Window appears on screen
- ✅ Click interaction works
- ✅ Keyboard shortcuts respond (F1)
- ✅ Screenshot capture
- ✅ Cleanup/termination

**Output**:
- Console log with pass/fail
- `screenshot_test.png` - GUI screenshot

### 2. `gui_automation_test.py` - Full Test Suite
**Purpose**: Comprehensive end-to-end testing
**Runtime**: ~2-3 minutes

```bash
python tests/gui_automation_test.py
```

**What it tests**:

**5-Step Wizard Flow**:
1. **Define Research** - Template selection, prompt composer
2. **Refine Filters** - Facets bar, results slider
3. **Review Configuration** - Review sheet verification
4. **Run Scraper** - UI state during execution
5. **Export Results** - Format selection, export button

**Additional Tests**:
- Wizard rail navigation (clicking step indicators)
- Keyboard shortcuts (Ctrl+N, Escape, F1)
- Live preview panel updates
- Accessibility features (Tab navigation)
- Toast notifications

**Output**:
- `test_report.txt` - Detailed timestamped log of all actions

## Safety Features

**FAILSAFE Protection**:
- Move mouse to **top-left corner** to abort test immediately
- Prevents runaway automation

**Pause Between Actions**:
- 0.5-1.0 second delay between commands
- Allows UI to update before next action

**Auto-Cleanup**:
- Terminates application on completion
- Closes app even if test fails

## Prerequisites

**Required**:
- Python 3.13+ with PyAutoGUI installed
- YouTube Research Platform application ready to run
- Display resolution: 1920x1080 recommended (tests use relative positioning)

**Installation**:
```bash
pip install pyautogui pillow
```

## Usage

### Quick Test (10 seconds)
```bash
cd "C:\Users\mike\OHiSee\OHiSee_Youtube_Transcipt Scraper"
python tests/quick_gui_test.py
```

### Full Test Suite (2-3 minutes)
```bash
python tests/gui_automation_test.py
```

### Do NOT:
- ❌ Move mouse during test execution
- ❌ Switch windows or applications
- ❌ Run tests while app is already open
- ❌ Run on different screen resolutions without adjustment

## Test Architecture

### YouTubeGUITester Class

**Key Methods**:
- `launch_app()` - Start application process
- `find_window()` - Locate window by title
- `click_relative(x%, y%, bounds)` - Click at percentage of window size
- `type_text(text)` - Simulate keyboard input
- `test_step*()` - Individual step test methods
- `run_full_test_suite()` - Execute all tests

**Coordinate System**:
- Uses **relative positioning** (0.0-1.0) instead of absolute pixels
- `click_relative(0.5, 0.5, bounds)` = center of window
- Adapts to different window sizes automatically

### Example: Custom Test

```python
from gui_automation_test import YouTubeGUITester

tester = YouTubeGUITester()
tester.launch_app()
window_bounds = tester.find_window()

# Custom interaction
tester.click_relative(0.3, 0.6, window_bounds)  # Click topic field
tester.type_text("my custom query")
pyautogui.press("enter")

tester.cleanup()
```

## Troubleshooting

**Issue**: "Window not found"
- **Solution**: Increase `time.sleep(3)` to `time.sleep(5)` after launch
- App may take longer to start on slower machines

**Issue**: Clicks miss targets
- **Solution**: Adjust relative coordinates in test methods
- Window layout may differ from expected

**Issue**: Unicode errors in console
- **Solution**: Already fixed - use `[PASS]` instead of emoji symbols

**Issue**: Test hangs
- **Solution**: Move mouse to corner (FAILSAFE), then debug specific step

## MCP Integration

This test suite uses the **MCP PyAutoGUI Server** (verified 2025-10-05):

**Configuration** (`C:\Users\mike\.cursor\mcp.json`):
```json
{
  "pyautogui": {
    "command": "python",
    "args": ["-m", "mcp_pyautogui_server"],
    "description": "Desktop automation using PyAutoGUI"
  }
}
```

**Capabilities**:
- 🖱️ Mouse control (click, move, drag)
- ⌨️ Keyboard input simulation
- 📸 Screen capture and image recognition
- 🪟 Window detection and activation

**Repository**: https://github.com/hetaoBackend/mcp-pyautogui-server

## Future Enhancements

- [ ] Add image recognition for button detection (eliminate coordinates)
- [ ] Integrate with CI/CD for automated regression testing
- [ ] Add performance metrics (step completion times)
- [ ] Create test fixtures for different screen resolutions
- [ ] Add video recording of test execution

## References

- **Project CLAUDE.md**: Full automation documentation
- **Global CLAUDE.md**: MCP PyAutoGUI verification details
- **PyAutoGUI Docs**: https://pyautogui.readthedocs.io
