# Components

All public types are prefixed `IOS`. Start from `IOSDesignTokens.neutral`,
modify the semantic light/dark colors, spacing, radii, typography or control
dimensions, then inject it with `.iosDesignTokens(tokens)`. Components read the
same environment value. The old `IOSTheme`, `IOSPalette`, `IOSSpacing`,
`IOSRadii`, and `.iosTheme(_:)` names remain as source-compatible aliases.
Keep each foreground/background pair legible; do not scatter new colors or
component measurements through screens. The token source is
`Sources/Evoloom/Tokens/DesignTokens.swift`; copying a component includes
this file automatically.

Component Views use ordinary SwiftUI `body` implementations. No macro product
is needed by the library or source copies. Bindings, actions, arbitrary child
Views and environment changes follow SwiftUI's normal update behavior. Do not
assume a performance improvement without profiling an integrating screen.

| Component | API | State and responsibility |
| --- | --- | --- |
| `IOSButton` | `IOSButton("Save", variant: .primary, size: .regular, isLoading: saving) { save() }` | Variants: primary, secondary, outline, ghost, destructive. The loading button disables itself. The caller must prevent concurrent work outside this view. For native destructive role use `Button("Delete", role: .destructive) { ... }.buttonStyle(IOSButtonStyle())`. |
| `IOSCard`, `IOSCardHeader` | `IOSCard { IOSCardHeader("Project", detail: "Summary"); Text("Content") }` | Container accepts arbitrary content. `cardForeground` is its default text style; explicitly styled children keep their style. Header detail uses `cardMutedForeground`. Set both colors against `card` for a custom palette. |
| `IOSBadge` | `IOSBadge("Ready", symbol: "checkmark", variant: .success)` | Noninteractive status; do not attach an action. |
| `IOSInput` | `IOSInput("Email", text: $email, placeholder: "name@example.com", error: error, keyboardType: .emailAddress, contentType: .emailAddress)` | A persistent label stays visible. Supports secure mode, hint, error and native focus behavior. Provide actionable error copy. `.disabled(true)` uses SwiftUI. |
| `IOSTextArea` | `IOSTextArea("Notes", text: $notes, hint: "Optional")` | Multiline native TextEditor with persistent label and error. |
| `IOSSeparator` | `IOSSeparator()` | Decorative and hidden from accessibility. |
| `IOSSwitch` | `IOSSwitch("Updates", isOn: $updates, detail: "On this device")` | Native Toggle owns interaction and VoiceOver state. The neutral dark on-track token is gray; a visible On/Off label and filled/empty circle distinguish states in dark mode. The cue also appears with Differentiate Without Color. |
| `IOSInlineAlert` | `IOSInlineAlert("Unavailable", message: "Try again.", variant: .error)` | Persistent inline message. Use SwiftUI `.alert` for an interrupting decision. |
| `IOSEmptyState` | `IOSEmptyState("No items", message: "Create one.") { IOSButton("Create") {} }` | Optional action; explain what can happen next. |
| `IOSSkeleton` | `IOSSkeleton(height: 20)` | Static, decorative and hidden from accessibility. Put a visible or accessible loading description beside it in the containing screen. |

`IOSSwitch` accepts optional `onStateLabel` and `offStateLabel`
`LocalizedStringKey` values. Their defaults are "On" and "Off"; supply
translations in the integrating app or pass localized labels, for example
`IOSSwitch("通知", isOn: $enabled, onStateLabel: "オン", offStateLabel: "オフ")`.
The status cue is visual; the native Toggle announces its state to VoiceOver.
Most other public APIs accept `String`. Localize dynamic values at the call site with
`String(localized:)` and supply a product String Catalog. Do not assume
placeholder text is a label. Native system controls provide their own
localization where applicable. Test both English and Japanese and add RTL
coverage when your product supports RTL. The app owns validation, persistence,
networking, navigation, loading state, and action deduplication.

Native Button, Toggle, TextField, SecureField and TextEditor provide the
control's interaction and state semantics. Decorative symbols are hidden.
Evoloom does not set a screen reading order, focus target or announcement
timing. The integrating product chooses contextual labels, descriptions,
headings, grouping and the final VoiceOver test. Use SwiftUI accessibility
modifiers at the integration site where the defaults do not fit the context.
Inline alert text remains separate so the screen can choose grouping; use the
system alert for an interrupting decision.
