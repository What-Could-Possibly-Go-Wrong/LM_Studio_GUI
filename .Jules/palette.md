## 2025-05-14 - Visual Focus for PyQt6 Buttons
**Learning:** When using custom stylesheets in PyQt6, the default focus rectangle for `QPushButton` may be lost or become invisible. Explicitly defining a `:focus` state in the stylesheet is critical for keyboard accessibility.
**Action:** Always include a `:focus` selector when styling interactive components in PyQt6 to ensure keyboard users can track their position.
