@testable import Evoloom
@testable import EvoloomReviewFixtures
import SnapshotTesting
import SwiftUI
import UIKit
import XCTest

@MainActor
final class ComponentSnapshots: XCTestCase {
    private let width: CGFloat = 390

    func testCatalogLight() {
        snapshot(catalog(), name: "catalog-light", height: 1500, scheme: .light)
    }

    func testCatalogDark() {
        snapshot(catalog(), name: "catalog-dark", height: 1500, scheme: .dark)
    }

    func testSwitchStatesDark() {
        let view = VStack(alignment: .leading, spacing: 16) {
            IOSSwitch("Notifications", isOn: .constant(true), detail: "Receive updates on this device.")
            IOSSeparator()
            IOSSwitch("Notifications", isOn: .constant(false), detail: "Receive updates on this device.")
        }
        snapshot(view, name: "switch-states-dark", height: 220, scheme: .dark)
        snapshot(view, name: "switch-states-dark-increased-contrast", height: 220, scheme: .dark, contrast: .increased)

        let japanese = VStack(alignment: .leading, spacing: 16) {
            IOSSwitch("通知", isOn: .constant(true), detail: "この端末で通知を受け取ります。", onStateLabel: "オン", offStateLabel: "オフ")
            IOSSeparator()
            IOSSwitch("通知", isOn: .constant(false), detail: "この端末で通知を受け取ります。", onStateLabel: "オン", offStateLabel: "オフ")
        }
        snapshot(japanese, name: "switch-states-dark-ja", height: 220, scheme: .dark, locale: "ja_JP")
    }

    func testCustomizedDesignTokens() {
        for scheme in [ColorScheme.light, .dark] {
            let tokens = customizedTokens()
            let view = VStack(alignment: .leading, spacing: tokens.spacing.md) {
                IOSButton("Save changes") {}
                IOSCard {
                    VStack(alignment: .leading, spacing: tokens.spacing.xs) {
                        IOSCardHeader("Project", detail: "Supporting card text stays legible.")
                        Text("Default card text")
                        Text("Explicit child color").foregroundStyle(scheme == .light ? .cyan : .blue)
                    }
                }
                IOSInput("Name", text: .constant("Alex"), hint: "Visible to collaborators.")
                IOSBadge("Ready", symbol: "checkmark", variant: .neutral)
            }
            snapshot(
                view, name: scheme == .light ? "customized-tokens" : "customized-tokens-dark",
                height: 450, scheme: scheme, tokens: tokens
            )
        }
    }

    func testInputs() {
        let longNotes = "Several lines of text about the project.\n" +
            "More notes that continue across the available width and onto another line."
        let view = VStack(alignment: .leading, spacing: 16) {
            IOSInput("Email", text: .constant("alex@example.com"), hint: "Used for receipts.", keyboardType: .emailAddress)
            IOSInput("Email", text: .constant("bad"), error: "Enter a valid email address.")
            IOSInput("Email", text: .constant("A very long address that must wrap or scroll@example.com"))
            IOSInput("Email", text: .constant("Disabled"), hint: "Unavailable now.").disabled(true)
            IOSTextArea("Notes", text: .constant(longNotes), hint: "Optional")
            IOSTextArea("Notes", text: .constant("Please check this value."), error: "Use fewer than 200 characters.")
            IOSTextArea("Notes", text: .constant("Editing is unavailable."), hint: "Read only for now.").disabled(true)
        }
        snapshot(view, name: "inputs-light", height: 930, scheme: .light)
        snapshot(view, name: "inputs-dark", height: 930, scheme: .dark)
    }

    func testCompactAndAccessibility() {
        let view = VStack(alignment: .leading, spacing: 16) {
            Text("Upcoming work").font(.title.bold())
            IOSCard {
                IOSCardHeader("A long project name that should wrap onto another line", detail: "Progress and context belong together.")
            }
            IOSInlineAlert("Please review", message: "A long explanation of the action needed before continuing.", variant: .error)
            IOSButton("Continue with the selected project") {}
            IOSBadge("Waiting for account verification and review", symbol: "clock", variant: .secondary)
            IOSEmptyState(
                "No matching projects were found",
                message: "Try a broader search or create a new project to continue with your work."
            )
        }
        snapshot(view, name: "compact-accessibility", width: 320, height: 1150, scheme: .light, category: .accessibilityMedium, contrast: .increased)
    }

    func testLocalized() {
        let view = VStack(alignment: .leading, spacing: 16) {
            IOSCard { IOSCardHeader("プロジェクト", detail: "続行する前に内容を確認してください。") }
            IOSButton("保存する") {}
            IOSEmptyState("項目がありません", message: "新しい項目を作成してください。")
        }
        snapshot(view, name: "locale-ja", height: 360, scheme: .light, locale: "ja_JP")
        let english = VStack(alignment: .leading, spacing: 16) {
            IOSCard { IOSCardHeader("Project", detail: "Review the content before continuing.") }
            IOSButton("Save") {}
            IOSEmptyState("No items", message: "Create a new item.")
        }
        snapshot(english, name: "locale-en", height: 360, scheme: .light, locale: "en_US")
    }

    func testReviewScreens() {
        snapshot(ReviewComponentsView(page: .controls), name: "review-components-controls-light", height: 700, scheme: .light, inset: false)
        snapshot(ReviewComponentsView(page: .controls), name: "review-components-controls-dark", height: 700, scheme: .dark, inset: false)
        snapshot(ReviewComponentsView(page: .feedback), name: "review-components-feedback-light", height: 600, scheme: .light, inset: false)
        snapshot(ReviewComponentsView(page: .feedback), name: "review-components-feedback-dark", height: 600, scheme: .dark, inset: false)
        snapshot(ReviewSettingsView(), name: "review-settings-light", height: 780, scheme: .light, inset: false)
        snapshot(ReviewSettingsView(), name: "review-settings-dark", height: 780, scheme: .dark, inset: false)
        snapshot(ReviewSettingsView(showError: true), name: "review-settings-error", height: 780, scheme: .light, inset: false)
        snapshot(
            ReviewSettingsView(longJapanese: true), name: "review-settings-narrow-ja", width: 320,
            height: 1050, scheme: .light, locale: "ja_JP", inset: false
        )
        snapshot(
            ReviewSettingsView(), name: "review-settings-large-text", height: 1050,
            scheme: .light, category: .accessibilityMedium, inset: false
        )
        snapshot(ReviewDetailView(), name: "review-detail-light", height: 660, scheme: .light, inset: false)
        snapshot(ReviewDetailView(), name: "review-detail-dark", height: 660, scheme: .dark, inset: false)
        snapshot(
            ReviewDetailView(longJapanese: true), name: "review-detail-ja-long", width: 320,
            height: 900, scheme: .light, locale: "ja_JP", inset: false
        )
    }

    func testCollectionCompactAccessibility() {
        snapshot(
            ExampleCollectionView(initialState: .normal), name: "collection-compact-accessibility", width: 320,
            height: 780, scheme: .light, category: .accessibilityMedium,
            contrast: .increased, inset: false
        )
    }

    private func customizedTokens() -> IOSDesignTokens {
        var tokens = IOSDesignTokens.neutral
        tokens.light.primary = .indigo
        tokens.light.primaryForeground = .white
        tokens.light.card = Color(red: 0.15, green: 0.10, blue: 0.25)
        tokens.light.cardForeground = Color(red: 1, green: 0.95, blue: 0.75)
        tokens.light.cardMutedForeground = Color(red: 0.83, green: 0.78, blue: 0.91)
        tokens.dark.card = Color(red: 1, green: 0.93, blue: 0.68)
        tokens.dark.cardForeground = Color(red: 0.20, green: 0.11, blue: 0.08)
        tokens.dark.cardMutedForeground = Color(red: 0.32, green: 0.21, blue: 0.14)
        tokens.spacing.md = 20
        tokens.radii.control = 16
        tokens.controls.minimumHeight = 48
        return tokens
    }

    private func catalog() -> some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Components").font(.title.bold())
            ForEach(IOSButtonVariant.allCases, id: \.self) { variant in
                IOSButton("Continue", variant: variant) {}
            }
            IOSButton("Saving", isLoading: true) {}
            IOSButton("Unavailable") {}.disabled(true)
            Button("Delete", role: .destructive) {}.buttonStyle(IOSButtonStyle())
            IOSCard {
                VStack(alignment: .leading, spacing: 12) {
                    IOSCardHeader("Project", detail: "A content container with an extended description.")
                    IOSSeparator()
                    IOSBadge("Ready", symbol: "checkmark", variant: .success)
                }
            }
            HStack {
                IOSBadge("Neutral")
                IOSBadge("Secondary", variant: .secondary)
                IOSBadge("Error", variant: .destructive)
            }
            IOSInput("Name", text: .constant("Alex"), hint: "Visible to collaborators.")
            IOSTextArea("Notes", text: .constant("A short note."))
            IOSSwitch("Notifications", isOn: .constant(true), detail: "Receive updates on this device.")
            IOSInlineAlert("Information", message: "Changes are saved locally.")
            IOSEmptyState("Nothing here yet", message: "Create an item to get started.") {
                IOSButton("Create item") {}
            }
            IOSSkeleton()
        }
    }

    private func snapshot(
        _ content: some View, name: String, width: CGFloat? = nil, height: CGFloat,
        scheme: ColorScheme, category: ContentSizeCategory = .medium,
        contrast: ColorSchemeContrast = .standard, locale: String = "en_US", inset: Bool = true,
        tokens: IOSDesignTokens = .neutral
    ) {
        let size = CGSize(width: width ?? self.width, height: height)
        let palette = tokens.paletteForSnapshot(scheme)
        let view = content
            .padding(inset ? 16 : 0)
            .frame(width: size.width, height: size.height, alignment: .topLeading)
            .background(palette)
            .iosDesignTokens(tokens)
            .environment(\.locale, Locale(identifier: locale))
            .environment(\.timeZone, TimeZone(secondsFromGMT: 0) ?? .current)
            .environment(\.sizeCategory, category)
            .preferredColorScheme(scheme)
        let host = UIHostingController(rootView: view)
        host.overrideUserInterfaceStyle = scheme == .dark ? .dark : .light
        host.view.frame = CGRect(origin: .zero, size: size)
        host.view.layoutIfNeeded()
        let traits = UITraitCollection(mutations: { traits in
            traits.displayScale = 3
            traits.accessibilityContrast = contrast == .increased ? .high : .normal
        })
        let root = URL(fileURLWithPath: #filePath)
            .deletingLastPathComponent().deletingLastPathComponent()
            .deletingLastPathComponent().deletingLastPathComponent()
        let isRecording = FileManager.default.fileExists(atPath: root.appendingPathComponent(".prepared/record-snapshots").path)
        var strategy = Snapshotting<UIViewController, UIImage>.image(
            precision: 1, perceptualPrecision: 1, size: size, traits: traits
        )
        strategy.diffing = exactImageDiffing(strategy.diffing, root: root, name: name)
        if isRecording {
            let message = verifySnapshot(
                of: host, as: strategy, named: name, record: true,
                testName: "components"
            )
            XCTAssertTrue(message?.contains("Record mode is on.") == true, message ?? "Snapshot recording failed")
        } else {
            assertSnapshot(
                of: host, as: strategy, named: name, record: false,
                testName: "components"
            )
        }
    }
}

private extension IOSDesignTokens {
    func paletteForSnapshot(_ scheme: ColorScheme) -> Color {
        scheme == .dark ? dark.background : light.background
    }
}
