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
    let longJapanese: Bool

    init(showError: Bool = false, longJapanese: Bool = false) {
        self.showError = showError
        self.longJapanese = longJapanese
        _displayName = State(initialValue: longJapanese ? "調査とリリースの確認事項" : "Alex Rivera")
        _email = State(initialValue: showError ? "invalid" : "alex@example.com")
    }

    private var emailError: String? {
        guard showError && !email.contains("@") else { return nil }
        return longJapanese ? "保存する前に、有効なメールアドレスを入力してください。" : "Enter a valid email address before saving."
    }

    var body: some View {
        NavigationStack {
            Form {
                Section {
                    IOSInput(
                        longJapanese ? "チーム全員に表示する名前" : "Display name", text: $displayName,
                        hint: longJapanese ? "共同作業の画面と通知に表示されます。" : "Shown to your team.",
                        appearance: .formRow
                    )
                    IOSInput(
                        longJapanese ? "メールアドレス" : "Email", text: $email,
                        hint: showError ? nil : (longJapanese ? "アカウントに関する通知に使用します。" : "Used for account notices."),
                        error: emailError,
                        keyboardType: .emailAddress, appearance: .formRow
                    )
                } header: {
                    Text(longJapanese ? "プロフィール" : "Profile")
                }
                Section {
                    IOSSwitch(
                        longJapanese ? "プロジェクトの更新通知" : "Project updates", isOn: $notifications,
                        detail: longJapanese ? "この端末で変更内容を受け取ります。" : "Receive changes on this device.",
                        onStateLabel: longJapanese ? "オン" : "On", offStateLabel: longJapanese ? "オフ" : "Off"
                    )
                    IOSInput(
                        longJapanese ? "ワークスペース" : "Workspace", text: .constant("Field notes"),
                        hint: longJapanese ? "チームの管理者が設定します。" : "Managed by your team.",
                        appearance: .formRow
                    )
                    .disabled(true)
                } header: {
                    Text(longJapanese ? "通知と管理" : "Preferences")
                } footer: {
                    IOSButton(
                        action: {},
                        label: {
                            Text(longJapanese ? "設定を保存" : "Save settings")
                                .frame(maxWidth: .infinity)
                        }
                    )
                    .disabled(showError && !email.contains("@"))
                }
            }
            .navigationTitle(longJapanese ? "設定" : "Settings")
        }
    }
}

struct ReviewDetailView: View {
    @Environment(\.iosDesignTokens) private var tokens
    @State private var title = ReviewCopy.project
    @State private var notes = "Capture findings, then agree on the next action."
    let longJapanese: Bool

    init(longJapanese: Bool = false) {
        self.longJapanese = longJapanese
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
                            IOSCardHeader(
                                longJapanese ? "プロジェクトの概要" : "Project overview",
                                detail: longJapanese ? "次のリリースに向けた調査と確認事項をまとめています。" : ReviewCopy.description
                            )
                            IOSBadge(longJapanese ? "進行中" : "In progress", symbol: "clock", variant: .secondary)
                        }
                    }
                    IOSInput(
                        longJapanese ? "タイトル" : "Title", text: $title,
                        hint: longJapanese ? "チーム内でわかる名前を付けてください。" : "Use a name your team recognizes."
                    )
                    IOSTextArea(
                        longJapanese ? "メモ" : "Notes", text: $notes,
                        hint: longJapanese ? "次に行うことをまとめてください。" : "Summarize the next step."
                    )
                    IOSButton(longJapanese ? "プロジェクトを保存" : "Save project") {}
                }
                .padding(tokens.spacing.md)
            }
            .navigationTitle(longJapanese ? "プロジェクトの詳細" : "Project details")
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

#Preview("Settings - narrow Japanese") {
    ReviewSettingsView(longJapanese: true)
        .environment(\.locale, Locale(identifier: "ja_JP"))
        .frame(width: 320)
}

#Preview("Settings - large text") {
    ReviewSettingsView()
        .environment(\.sizeCategory, .accessibilityMedium)
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
