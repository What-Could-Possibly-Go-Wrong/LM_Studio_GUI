## 2025-05-15 - [Feedback Loops in Desktop Apps]
**Learning:** In desktop GUI applications, background operations like saving or graph execution need immediate visual confirmation. Relying solely on log files (debug.log) is a poor UX as the user is left wondering if the action succeeded.
**Action:** Always implement a QStatusBar or similar transient notification system for critical actions.

## 2025-05-15 - [Discoverability of Shortcuts]
**Learning:** Keyboard shortcuts improve accessibility and power-user efficiency, but are hard to discover if not explicitly mentioned in tooltips.
**Action:** Append the keyboard shortcut in parentheses to the button tooltip (e.g., 'Save (Ctrl+S)') to aid discovery.
