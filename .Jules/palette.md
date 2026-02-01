## 2025-05-14 - [Focus States & Keyboard Discoverability]
**Learning:** When using custom stylesheets in PyQt6, default focus indicators for buttons are often lost. Additionally, keyboard shortcuts are powerful but invisible unless explicitly hinted.
**Action:** Always define a `:focus` selector in QSS for interactive elements. Include shortcut hints in parentheses within tooltips (e.g., "Action (Ctrl+Key)") to improve discoverability.

## 2025-05-14 - [Headless UI Verification]
**Learning:** Capturing screenshots of PyQt6 applications in a headless environment (xvfb) requires processing events and a small delay to ensure rendering is complete, otherwise screenshots may appear black.
**Action:** Use `app.processEvents()` and `time.sleep(0.1)` before `screen.grabWindow()` in verification scripts.
