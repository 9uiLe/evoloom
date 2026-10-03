# Components

All public types are prefixed `IOS`. `IOSTheme.neutral` is injected with
`.iosTheme(theme)`. A screen can customize either palette and shared spacing
or radii before injection. Do not scatter new colors through screens.

| Component | API | State and responsibility |
| --- | --- | --- |
| `IOSButton` | `IOSButton("Save", variant: .primary, size: .regular, isLoading: saving) { save() }` | Variants: primary, secondary, outline, ghost, destructive. The loading button disables itself. The caller must prevent concurrent work outside this view. For native destructive role use `Button("Delete", role: .destructive) { ... }.buttonStyle(IOSButtonStyle())`. |
| `IOSCard`, `IOSCardHeader` | `IOSCard { IOSCardHeader("Project", detail: "Summary"); Text("Content") }` | Container accepts arbitrary content; no product data model. |
| `IOSBadge` | `IOSBadge("Ready", symbol: "checkmark", variant: .success)` | Noninteractive status; do not attach an action. |
| `IOSInput` | `IOSInput("Email", text: $email, placeholder: "name@example.com", error: error, keyboardType: .emailAddress, contentType: .emailAddress)` | A persistent label stays visible. Supports secure mode, hint, error and native focus behavior. Provide actionable error copy. `.disabled(true)` uses SwiftUI. |
| `IOSTextArea` | `IOSTextArea("Notes", text: $notes, hint: "Optional")` | Multiline native TextEditor with persistent label and error. |
| `IOSSeparator` | `IOSSeparator()` | Decorative and hidden from accessibility. |
| `IOSSwitch` | `IOSSwitch("Updates", isOn: $updates, detail: "On this device")` | Native Toggle owns interaction and VoiceOver state. |
| `IOSInlineAlert` | `IOSInlineAlert("Unavailable", message: "Try again.", variant: .error)` | Persistent inline message. Use SwiftUI `.alert` for an interrupting decision. |
| `IOSEmptyState` | `IOSEmptyState("No items", message: "Create one.") { IOSButton("Create") {} }` | Optional action; explain what can happen next. |
| `IOSSkeleton` | `IOSSkeleton(height: 20)` | Static placeholder; put a spoken loading label on its parent. |

The public APIs accept `String`. Localize dynamic values at the call site with
`String(localized:)` and supply a product String Catalog. Do not assume
placeholder text is a label. Native system controls provide their own
localization where applicable. Test both English and Japanese and add RTL
coverage when your product supports RTL. The app owns validation, persistence,
networking, navigation, loading state, and action deduplication.
