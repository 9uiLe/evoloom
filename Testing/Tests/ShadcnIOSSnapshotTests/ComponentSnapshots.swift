import ShadcnIOS
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

    func testInputs() {
        let view = VStack(alignment: .leading, spacing: 16) {
            IOSInput("Email", text: .constant("alex@example.com"), hint: "Used for receipts.", keyboardType: .emailAddress)
            IOSInput("Email", text: .constant("bad"), error: "Enter a valid email address.")
            IOSInput("Email", text: .constant("A very long address that must wrap or scroll@example.com"))
            IOSInput("Email", text: .constant("Disabled"), hint: "Unavailable now.").disabled(true)
            IOSTextArea("Notes", text: .constant("Several lines of text.\nMore notes."), hint: "Optional")
            IOSTextArea("Notes", text: .constant("Please check this value."), error: "Use fewer than 200 characters.")
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
        }
        snapshot(view, name: "compact-accessibility", width: 320, height: 650, scheme: .light, category: .accessibilityMedium, contrast: .increased)
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

    func testRepresentativeScreen() {
        snapshot(collection(), name: "collection-light", height: 780, scheme: .light, inset: false)
        snapshot(
            collection(), name: "collection-compact-accessibility", width: 320,
            height: 780, scheme: .light, category: .accessibilityMedium,
            contrast: .increased, inset: false
        )
        snapshot(collection(), name: "collection-dark", height: 780, scheme: .dark, inset: false)
    }

    private func collection() -> some View {
        VStack(alignment: .leading, spacing: 0) {
            Text("Collection").font(.largeTitle.bold()).padding(16)
            List {
                Section("Upcoming") {
                    Text("Design notes")
                    Text("Release checklist")
                }
                Section("Status") {
                    IOSInlineAlert("Ready to review", message: "Two items are available.")
                }
            }
        }
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
        contrast: ColorSchemeContrast = .standard, locale: String = "en_US", inset: Bool = true
    ) {
        let size = CGSize(width: width ?? self.width, height: height)
        let palette = IOSTheme.neutral.paletteForSnapshot(scheme)
        let view = content
            .padding(inset ? 16 : 0)
            .frame(width: size.width, height: size.height, alignment: .topLeading)
            .background(palette)
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
        let imageDiffing = strategy.diffing
        strategy.diffing = Diffing<UIImage>(toData: imageDiffing.toData, fromData: imageDiffing.fromData) { expected, actual in
            guard let old = pixels(expected), let new = pixels(actual) else {
                return ("Image pixels could not be read", [])
            }
            guard old.width == new.width, old.height == new.height, old.bytes == new.bytes else {
                let directory = root.appendingPathComponent("TestResults/SnapshotDiffs/\(name)")
                try? FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
                try? expected.pngData()?.write(to: directory.appendingPathComponent("expected.png"))
                try? actual.pngData()?.write(to: directory.appendingPathComponent("actual.png"))
                if let image = difference(old: old, new: new) {
                    try? image.pngData()?.write(to: directory.appendingPathComponent("diff.png"))
                }
                return ("Pixel difference for \(name). Inspect expected, actual and diff in \(directory.path)", [])
            }
            return nil
        }
        assertSnapshot(
            of: host, as: strategy,
            named: name, record: isRecording,
            testName: "components"
        )
    }
}

private struct PixelImage {
    let width: Int
    let height: Int
    let bytes: [UInt8]
}

private func pixels(_ image: UIImage) -> PixelImage? {
    guard let source = image.cgImage else { return nil }
    let width = source.width
    let height = source.height
    var bytes = [UInt8](repeating: 0, count: width * height * 4)
    let success = bytes.withUnsafeMutableBytes { buffer in
        guard let context = CGContext(
            data: buffer.baseAddress, width: width, height: height,
            bitsPerComponent: 8, bytesPerRow: width * 4,
            space: CGColorSpaceCreateDeviceRGB(),
            bitmapInfo: CGImageAlphaInfo.premultipliedLast.rawValue
        ) else { return false }
        context.draw(source, in: CGRect(x: 0, y: 0, width: width, height: height))
        return true
    }
    return success ? PixelImage(width: width, height: height, bytes: bytes) : nil
}

private func difference(old: PixelImage, new: PixelImage) -> UIImage? {
    guard old.width == new.width, old.height == new.height else { return nil }
    var bytes = [UInt8](repeating: 255, count: old.bytes.count)
    for index in stride(from: 0, to: bytes.count, by: 4) {
        let changed = (0 ..< 4).contains { old.bytes[index + $0] != new.bytes[index + $0] }
        if changed {
            bytes[index] = 255
            bytes[index + 1] = 0
            bytes[index + 2] = 80
        }
    }
    guard let provider = CGDataProvider(data: Data(bytes) as CFData),
          let image = CGImage(
              width: old.width, height: old.height, bitsPerComponent: 8, bitsPerPixel: 32,
              bytesPerRow: old.width * 4, space: CGColorSpaceCreateDeviceRGB(),
              bitmapInfo: CGBitmapInfo(rawValue: CGImageAlphaInfo.premultipliedLast.rawValue),
              provider: provider, decode: nil, shouldInterpolate: false, intent: .defaultIntent
          ) else { return nil }
    return UIImage(cgImage: image)
}

private extension IOSTheme {
    func paletteForSnapshot(_ scheme: ColorScheme) -> Color {
        scheme == .dark ? dark.background : light.background
    }
}
