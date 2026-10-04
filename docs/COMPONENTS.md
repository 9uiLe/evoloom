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

All component View types use `@AutoEquatableView`. `IOSBadge`,
`IOSCardHeader`, `IOSInlineAlert`, `IOSSeparator` and `IOSSkeleton` have only
comparable parent inputs and get an equality boundary. Parent updates with
equal inputs can skip their content evaluation; SwiftUI environment changes
still invalidate their content. `IOSButton`, `IOSCard`, `IOSEmptyState`,
`IOSInput`, `IOSTextArea` and `IOSSwitch` retain a normal `body` because they
store an action, arbitrary child View, or Binding. This protects changed
callbacks, child content and bound values. `IOSButtonStyle` is a `ButtonStyle`,
not a View, so the macro does not apply to it. A macro attachment alone is not
a guarantee of fewer updates; profile the composed screen before relying on a
performance claim. See the [macro contract](https://github.com/9uiLe/swift-app-macros/blob/0.4.0/docs/auto-equatable-view.md).

| Component | API | State and responsibility |
| --- | --- | --- |
| `IOSButton` | `IOSButton("Save", variant: .primary, size: .regular, isLoading: saving) { save() }` | Variants: primary, secondary, outline, ghost, destructive. The loading button disables itself. The caller must prevent concurrent work outside this view. For native destructive role use `Button("Delete", role: .destructive) { ... }.buttonStyle(IOSButtonStyle())`. |
| `IOSCard`, `IOSCardHeader` | `IOSCard { IOSCardHeader("Project", detail: "Summary"); Text("Content") }` | Container accepts arbitrary content; no product data model. |
| `IOSBadge` | `IOSBadge("Ready", symbol: "checkmark", variant: .success)` | Noninteractive status; do not attach an action. |
| `IOSInput` | `IOSInput("Email", text: $email, placeholder: "name@example.com", error: error, keyboardType: .emailAddress, contentType: .emailAddress)` | A persistent label stays visible. Supports secure mode, hint, error and native focus behavior. Provide actionable error copy. `.disabled(true)` uses SwiftUI. |
| `IOSTextArea` | `IOSTextArea("Notes", text: $notes, hint: "Optional")` | Multiline native TextEditor with persistent label and error. |
| `IOSSeparator` | `IOSSeparator()` | Decorative and hidden from accessibility. |
| `IOSSwitch` | `IOSSwitch("Updates", isOn: $updates, detail: "On this device")` | Native Toggle owns interaction and VoiceOver state. Its on-track background uses `toggleOnBackground`; the neutral dark token is gray. |
| `IOSInlineAlert` | `IOSInlineAlert("Unavailable", message: "Try again.", variant: .error)` | Persistent inline message. Use SwiftUI `.alert` for an interrupting decision. |
| `IOSEmptyState` | `IOSEmptyState("No items", message: "Create one.") { IOSButton("Create") {} }` | Optional action; explain what can happen next. |
| `IOSSkeleton` | `IOSSkeleton(height: 20)` | Static placeholder; put a spoken loading label on its parent. |

The public APIs accept `String`. Localize dynamic values at the call site with
`String(localized:)` and supply a product String Catalog. Do not assume
placeholder text is a label. Native system controls provide their own
localization where applicable. Test both English and Japanese and add RTL
coverage when your product supports RTL. The app owns validation, persistence,
networking, navigation, loading state, and action deduplication.
