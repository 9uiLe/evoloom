# Design rules

This is a design starting point, not a claim that screenshots establish good design.
Use native `NavigationStack`, `TabView`, `List`, `Form`, `searchable`, pickers,
menus, sheets, alerts and toggles for navigation and system interaction.
The custom components cover repeated visual decisions that those controls do
not express together: semantic color pairs, labeled fields, status, and loading.

Use `IOSTheme` colors by meaning. Choose foreground and background as a pair;
check contrast after any theme edit. Light and dark palettes are explicit.
Spacing tokens are 4, 8, 12, 16, 24 and 32 pt. Do not replace native List or
Form internal spacing. Radii are control, card and badge tokens. Text uses
system text styles and grows with Dynamic Type. Primary actions keep a 44 pt
minimum height and grow with text. Avoid wrapping every section in a card.

State must be legible without color: error text should say what to fix,
loading should explain progress to assistive technology, and badges should
include words. Skeleton is static and decorative; announce loading on its
parent. Respect Reduce Motion; no animation is required by these components.
Use `Button(role: .destructive)` with `IOSButtonStyle` for destructive actions.
The inline alert is content inside a screen; use the native alert for blocking
decisions. Keep native back gestures, safe areas and keyboard behavior.

For AI screen generation: start with the user's goal, the information order,
the single primary action, and the native iOS container. Use these tokens and
components only where they solve a repeated visual need. Check Japanese and
English length, a narrow width, dark mode, large text, Increased Contrast,
VoiceOver reading order, keyboard operation and double submission. Label
design preferences as preferences, untested outcomes as hypotheses, and
observed behavior as evidence.

References: [shadcn/ui documentation](https://ui.shadcn.com/docs),
[shadcn/ui theming](https://ui.shadcn.com/docs/theming),
[Apple SwiftUI documentation](https://developer.apple.com/documentation/swiftui),
and [Apple's 2024 accessibility session](https://developer.apple.com/videos/play/wwdc2024/10074/).
These informed design choices; this project's behavior is verified by its own
builds, tests and images. The linked note.com article could not be read from
the development environment, so its claims were not used as evidence.
