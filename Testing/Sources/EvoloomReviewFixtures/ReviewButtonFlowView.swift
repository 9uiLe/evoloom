import Evoloom
import SwiftUI

enum ReviewButtonPhase {
    case ready, running, completed, failed
}

/// Deterministic, development-only control of a simulated operation.
struct ReviewButtonFlowView: View {
    @Environment(\.iosDesignTokens) private var tokens
    @State private var phase: ReviewButtonPhase
    @State private var runsStarted: Int
    @State private var externallyDisabled: Bool
    let longJapanese: Bool

    init(initialPhase: ReviewButtonPhase = .ready, externallyDisabled: Bool = false, longJapanese: Bool = false) {
        _phase = State(initialValue: initialPhase)
        _runsStarted = State(initialValue: initialPhase == .ready ? 0 : 1)
        _externallyDisabled = State(initialValue: externallyDisabled)
        self.longJapanese = longJapanese
    }

    var body: some View {
        NavigationStack {
            ScrollView {
                VStack(alignment: .leading, spacing: tokens.spacing.lg) {
                    Text(longJapanese ? "処理中の操作と結果を、同じ画面で確認します。" : "Review the action, progress, and result in one place.")
                        .font(tokens.typography.supporting)
                    IOSBadge(status, symbol: symbol, variant: variant)
                    Text(longJapanese ? "開始回数: \(runsStarted)" : "Runs started: \(runsStarted)")
                        .font(tokens.typography.supporting)
                    IOSButton(isLoading: phase == .running, action: {
                        runsStarted += 1
                        phase = .running
                    }, label: {
                        Text(actionTitle).frame(maxWidth: .infinity)
                    })
                    .disabled(externallyDisabled)
                    IOSSwitch(
                        longJapanese ? "外側から操作を無効化" : "Disable action from parent",
                        isOn: $externallyDisabled
                    )
                    if phase == .running {
                        VStack(alignment: .leading, spacing: tokens.spacing.sm) {
                            IOSButton(longJapanese ? "成功を確定" : "Complete successfully", variant: .secondary) {
                                phase = .completed
                            }
                            IOSButton(longJapanese ? "失敗を確定" : "Finish with error", variant: .outline) {
                                phase = .failed
                            }
                        }
                    } else if phase == .completed {
                        Text(longJapanese ? "模擬処理が完了しました。データは保存されません。" : "Simulated operation completed. No data was saved.")
                            .font(tokens.typography.supporting)
                    } else if phase == .failed {
                        IOSInlineAlert(
                            longJapanese ? "模擬処理に失敗" : "Simulated operation failed",
                            message: longJapanese ? "データは保存されませんでした。再試行できます。" : "No data was saved. Try again.",
                            variant: .error
                        )
                    }
                }
                .padding(tokens.spacing.md)
            }
            .navigationTitle(longJapanese ? "ボタンの状態" : "Button states")
        }
    }

    private var actionTitle: String {
        switch phase {
        case .ready, .running: longJapanese ? "確認を実行する" : "Run review"
        case .completed: longJapanese ? "もう一度実行" : "Run again"
        case .failed: longJapanese ? "再試行" : "Try again"
        }
    }

    private var status: String {
        switch phase {
        case .ready: longJapanese ? "実行前" : "Ready"
        case .running: longJapanese ? "処理中" : "Processing"
        case .completed: longJapanese ? "完了" : "Completed"
        case .failed: longJapanese ? "失敗" : "Failed"
        }
    }

    private var symbol: String {
        switch phase {
        case .ready: "circle"
        case .running: "hourglass"
        case .completed: "checkmark.circle"
        case .failed: "exclamationmark.circle"
        }
    }

    private var variant: IOSBadgeVariant {
        switch phase {
        case .ready, .running: .secondary
        case .completed: .success
        case .failed: .destructive
        }
    }
}

#Preview("Button states - ready") {
    ReviewButtonFlowView()
}

#Preview("Button states - loading") {
    ReviewButtonFlowView(initialPhase: .running)
}

#Preview("Button states - failed Japanese") {
    ReviewButtonFlowView(initialPhase: .failed, longJapanese: true)
        .environment(\.locale, Locale(identifier: "ja_JP"))
}
