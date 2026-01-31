## 2025-05-15 - Explicit Focus Indicators in PyQt6 QSS
**Learning:** Applying custom stylesheets to interactive widgets like `QPushButton` or `QLineEdit` in PyQt6 can remove the default operating system focus indicators. This breaks keyboard accessibility as users cannot see which element is active.
**Action:** Always include a `:focus` selector in the QSS when styling interactive elements to ensure a clear, high-contrast focus border or background change is visible.
