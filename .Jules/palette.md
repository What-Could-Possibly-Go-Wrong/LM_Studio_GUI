## 2025-05-15 - [Smooth Dynamic Connections & Accessibility]
**Learning:** In a node-based editor, static connection lines that don't follow node movement significantly break the user's mental model and flow. Using `itemChange` with `ItemScenePositionHasChanged` in child items (Ports) is a robust way to trigger updates in parent-less items (Connections).
**Action:** Always implement dynamic line updates when adding graph functionality.

**Learning:** When using custom QSS for `QPushButton`, the default focus indicator is often lost. This is a critical accessibility issue for keyboard users.
**Action:** Explicitly define a `:focus` selector in the stylesheet to maintain keyboard visibility.

**Learning:** Tooltips that explicitly mention keyboard shortcuts (e.g., "Save (Ctrl+S)") significantly improve discoverability and empower users to transition from mouse to keyboard interaction.
**Action:** Always include shortcut hints in tooltips for core actions.
