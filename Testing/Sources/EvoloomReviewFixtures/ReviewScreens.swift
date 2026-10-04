import Evoloom
import SwiftUI

/// Fixed examples for design review. This target is not a product dependency.
enum ReviewCopy {
    static let project = "Field notes"
    static let description = "A shared place for research and release decisions."
    static let longJapanese = "調査結果と次のリリースに向けた確認事項を、チーム全員が同じ文脈で読めるようにまとめます。"
}

enum ReviewComponentPage {
    case controls, feedback
}

struct ReviewComponentsView: View {
    @Environment(\.iosDesignTokens) private var tokens
    let page: ReviewComponentPage

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: tokens.spacing.lg) {
                Text(page == .controls ? "Controls" : "Content and feedback")
                    .font(.largeTitle.bold())
                switch page {
                case .controls:
                    controls
                case .feedback:
                    feedback
                }
            }
            .padding(tokens.spacing.md)
        }
    }

    private var controls: some View {
        VStack(alignment: .leading, spacing: tokens.spacing.md) {
            IOSInput("Name", text: .constant("Alex Rivera"), hint: "Visible to collaborators.")
            IOSInput("Email", text: .constant("invalid"), error: "Enter a valid email address.")
            IOSSwitch("Notifications", isOn: .constant(true), detail: "Receive project updates.")
            IOSSwitch("Weekly digest", isOn: .constant(false), detail: "A summary every Friday.")
            IOSSeparator()
            IOSButton("Save changes") {}
            IOSButton("Preview", variant: .secondary) {}
            IOSButton("Unavailable") {}.disabled(true)
            IOSButton("Saving", isLoading: true) {}
        }
    }

    private var feedback: some View {
        VStack(alignment: .leading, spacing: tokens.spacing.md) {
            IOSCard {
                IOSCardHeader(ReviewCopy.project, detail: ReviewCopy.description)
            }
            HStack(spacing: tokens.spacing.xs) {
                IOSBadge("Ready", symbol: "checkmark", variant: .success)
                IOSBadge("Draft", variant: .secondary)
                IOSBadge("Needs review", variant: .destructive)
            }
            IOSInlineAlert("Review needed", message: "Check the project details before sharing.", variant: .error)
            IOSEmptyState("No recent activity", message: "Updates will appear here when the team adds them.")
            Text("Loading preview")
                .font(tokens.typography.supporting)
            IOSSkeleton()
        }
    }
}

struct ReviewSettingsView: View {
    @State private var displayName = "Alex Rivera"
    @State private var email = "alex@example.com"
    @State private var notifications = true
    let showError: Bool

    init(showError: Bool = false) {
        self.showError = showError
        _email = State(initialValue: showError ? "invalid" : "alex@example.com")
    }

    var body: some View {
        NavigationStack {
            Form {
                Section {
                    IOSInput("Display name", text: $displayName, hint: "Shown to your team.")
                    IOSInput(
                        "Email", text: $email, hint: showError ? nil : "Used for account notices.",
                        error: showError && !email.contains("@") ? "Enter a valid email address before saving." : nil,
                        keyboardType: .emailAddress
                    )
                } header: {
                    Text("Profile")
                }
                Section {
                    IOSSwitch("Project updates", isOn: $notifications, detail: "Receive changes on this device.")
                    IOSInput("Workspace", text: .constant("Field notes"), hint: "Managed by your team.")
                        .disabled(true)
                } header: {
                    Text("Preferences")
                }
                Section {
                    IOSButton("Save settings") {}
                        .frame(maxWidth: .infinity)
                        .disabled(showError && !email.contains("@"))
                }
            }
            .navigationTitle("Settings")
        }
    }
}

struct ReviewDetailView: View {
    @Environment(\.iosDesignTokens) private var tokens
    @State private var title = ReviewCopy.project
    @State private var notes = "Capture findings, then agree on the next action."

    init(longJapanese: Bool = false) {
        if longJapanese {
            _title = State(initialValue: "調査ノート")
            _notes = State(initialValue: ReviewCopy.longJapanese)
        }
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: tokens.spacing.lg) {
                    IOSCard {
                        VStack(alignment: .leading, spacing: tokens.spacing.md) {
                            IOSCardHeader("Project overview", detail: ReviewCopy.description)
                            IOSSeparator()
                            IOSBadge("In progress", symbol: "clock", variant: .secondary)
                        }
                    }
                    IOSInput("Title", text: $title, hint: "Use a name your team recognizes.")
                    IOSTextArea("Notes", text: $notes, hint: "Summarize the next step.")
                    IOSButton("Save project") {}
                }
                .padding(tokens.spacing.md)
            }
            .navigationTitle(title)
        }
    }
}

#Preview("Components - controls - light") {
    ReviewComponentsView(page: .controls).preferredColorScheme(.light)
}

#Preview("Components - controls - dark") {
    ReviewComponentsView(page: .controls).preferredColorScheme(.dark)
}

#Preview("Components - feedback - light") {
    ReviewComponentsView(page: .feedback).preferredColorScheme(.light)
}

#Preview("Components - feedback - dark") {
    ReviewComponentsView(page: .feedback).preferredColorScheme(.dark)
}

#Preview("Settings - light") {
    ReviewSettingsView().preferredColorScheme(.light)
}

#Preview("Settings - dark") {
    ReviewSettingsView().preferredColorScheme(.dark)
}

#Preview("Settings - error") {
    ReviewSettingsView(showError: true).preferredColorScheme(.light)
}

#Preview("Detail - light") {
    ReviewDetailView().preferredColorScheme(.light)
}

#Preview("Detail - dark") {
    ReviewDetailView().preferredColorScheme(.dark)
}

#Preview("Detail - narrow Japanese") {
    ReviewDetailView(longJapanese: true)
        .environment(\.locale, Locale(identifier: "ja_JP"))
        .frame(width: 320)
}
