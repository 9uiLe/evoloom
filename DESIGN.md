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
`IOSCard` sets `cardForeground` as the default foreground for child content;
an explicitly styled child keeps its own style. `IOSCardHeader` uses
`cardForeground` for its title and `cardMutedForeground` for supporting text.
The latter defaults to `cardForeground` in a newly constructed palette, so a
custom card does not inherit a muted color intended for the screen background.
The neutral palettes specify a distinct card supporting color. Check both
card text pairs against `card` when customizing a theme. A child that selects
its own text color, including `mutedForeground`, must also be checked against
the card surface. Badge, Input and Inline Alert use their own token pairs;
native List and Picker surfaces use system colors.

| Token pair or value | Rendered by |
| --- | --- |
| `background` / `foreground` | Input and TextArea surfaces and text, outline/ghost Button text, Switch status and informational Inline Alert text. These tokens do not paint the whole screen automatically. |
| `card` / `cardForeground` / `cardMutedForeground` | Card surface, default child text and Header text. |
| `primary` / `primaryForeground`, `secondary` / `secondaryForeground`, `destructive` / `destructiveForeground` | Button and Badge variants; focus and destructive states use their corresponding semantic roles. |
| `muted` / `mutedForeground`, `success` / `successForeground` | Disabled or supporting component content, Inline Alert surface, Skeleton and status Badge. |
| `border`, `input`, `toggleOnBackground` | Component outlines, input outlines and the native Toggle's selected track. |
`toggleOnBackground` colors the native Toggle track when it is on; the neutral
dark value is gray. In dark appearance, `IOSSwitch` also shows an On/Off label
and a filled or empty circle next to the setting name. The native thumb still
moves, while the extra cues separate similar gray tracks without requiring a
new switch implementation. The visual status is hidden from accessibility so
the native Toggle remains responsible for its spoken state. The same cue
appears in light appearance when Differentiate Without Color is enabled.
`IOSControlTokens` define the 44 pt minimum operation height, editor and
skeleton heights, separator and border thickness, and press opacity. Inject
the complete value through `.iosDesignTokens(tokens)` so nested components
use one decision set. Keep screen-specific layout choices in the screen.
Avoid wrapping every section in a card.

Components use ordinary SwiftUI `body` implementations. The former macro
comparison boundary applied to five display-only components; components with
Bindings, actions or child Views already used its ordinary-body fallback.
Keeping the macro made every copied target depend on a compiler plugin and
swift-syntax even when it could not skip updates. Source copies now have no
external Swift dependency. This change does not claim a measured performance
gain or loss; profile an integrating screen before adding update suppression.

| Macro approach | Effect and maintenance cost |
| --- | --- |
| Keep it required | Five display-only views gain a comparison boundary; the other six fall back to ordinary `body`. Every library and copy consumer needs the compiler plugin, and the five views depend on `EquatableBodyView` at runtime. |
| Make it optional in copied files | Consumers could skip the plugin, but generated plain Swift and macro source would be two component variants to review and test after every edit. |
| Use ordinary SwiftUI `body` (current) | One readable source path covers Package and copies, with no external runtime or compiler plugin. The five comparison boundaries are removed; performance impact is unmeasured. |

State must be legible without color: error text should say what to fix,
loading should explain progress to assistive technology, and badges should
include words. Skeleton is static and decorative. A screen supplies a visible
or accessible description of what is loading and decides when to announce
changes or move focus. Respect Reduce Motion; no animation is required by
these components.
Use `Button(role: .destructive)` with `IOSButtonStyle` for destructive actions.
The inline alert is content inside a screen; use the native alert for blocking
decisions. Keep native back gestures, safe areas and keyboard behavior.

Evoloom owns repeated component visuals and preserves native control labels,
values, states and actions. The product owns screen hierarchy, flow, contextual
labels, reading order, grouping, announcements, focus movement and final
VoiceOver validation. Component modifiers remain available for those choices;
decorative symbols and skeleton shapes are hidden from accessibility. The
component colors style Evoloom surfaces and text; List, NavigationStack,
Picker, searchable, sheets and system alerts retain their system appearance
and behavior. A product may set a screen-level tint where its context needs it.

When an integrating product finds a repeatable visual need, record the screen,
user task, observed issue and validation method before changing a token or
component rule. Add a shared rule only after checking another applicable
context and both light and dark appearances. Keep a single-product layout
decision in that product.

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

For the dark switch adjustment, [Apple's toggle guidance](https://developer.apple.com/design/human-interface-guidelines/toggles)
calls for a clear state difference beyond color and recommends the native iOS
switch. [Google Material](https://m2.material.io/components/switches)
also directs iOS implementations to use the platform switch.
[IBM Carbon](https://www.carbondesignsystem.com/building-blocks/core/components/toggle/guidelines)
uses state text and a checked small toggle;
[Microsoft Fluent](https://fluent2.microsoft.design/components/web/react/core/switch/usage/)
keeps the setting label adjacent to the switch. Evoloom uses those as design
references, not as code sources. Its gray palette is an Evoloom choice; the
status label and glyph address the observed dark-mode ambiguity.
