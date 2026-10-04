# Evoloom design rules

Evoloom starts with consistent design decisions that can evolve with an
integrating product. Source-owned components share these rules, while screen
structure and user flows remain product decisions. Screenshots detect visual
regressions; they do not by themselves establish good design.
Use native `NavigationStack`, `TabView`, `List`, `Form`, `searchable`, pickers,
menus, sheets, alerts and toggles for navigation and system interaction.
The custom components cover repeated visual decisions that those controls do
not express together: semantic color pairs, labeled fields, status, and loading.

`IOSDesignTokens` is the source of truth for repeated visual choices. Its
`light` and `dark` `IOSColorTokens` are semantic colors: choose foreground and
background as a pair and check contrast after edits. `IOSSpacingTokens` are
4, 8, 12, 16, 24 and 32 pt; do not replace native List or Form internal
spacing. `IOSRadiusTokens` define control, card and badge corners.
`IOSTypographyTokens` use system text styles so Dynamic Type can grow them.
`toggleOnBackground` colors the native Toggle track when it is on; the neutral
dark value is gray so the white thumb and track remain distinguishable.
`IOSControlTokens` define the 44 pt minimum operation height, editor and
skeleton heights, separator and border thickness, and press opacity. Inject
the complete value through `.iosDesignTokens(tokens)` so nested components
use one decision set. Keep screen-specific layout choices in the screen.
Avoid wrapping every section in a card.

`@AutoEquatableView` is an implementation rule for component Views. Comparable
display inputs may skip repeat parent updates. Bindings, actions and arbitrary
child Views must keep updating, so those components use the macro's ordinary
body fallback. Do not sacrifice current values or actions to obtain an
equality boundary. SwiftUI environment values remain under SwiftUI's
invalidation mechanism. Confirm any claimed performance gain with a measured
screen, while preserving the visual and accessibility checks below.

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
