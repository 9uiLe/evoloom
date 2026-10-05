import EvoloomReviewFixtures
import SnapshotTesting
import SwiftUI
import UIKit
import XCTest

@MainActor
final class HostedCollectionTests: XCTestCase {
    private static var captureSequence = 0

    func testCollectionLight() {
        capture(.normal, scheme: .light, name: "collection-light")
    }

    func testCollectionDark() {
        capture(.normal, scheme: .dark, name: "collection-dark")
    }

    func testCollectionEmpty() {
        capture(.empty, scheme: .light, name: "collection-empty")
    }

    func testCollectionLoading() {
        capture(.loading, scheme: .light, name: "collection-loading")
    }

    func testCollectionError() {
        capture(.error, scheme: .light, name: "collection-error")
    }

    private func capture(_ state: CollectionState, scheme: ColorScheme, name: String) {
        guard let scene = UIApplication.shared.connectedScenes.compactMap({ $0 as? UIWindowScene }).first,
              let window = scene.windows.first(where: \.isKeyWindow)
        else {
            XCTFail("Hosted snapshots require a key window in a connected window scene")
            return
        }
        XCTAssertEqual(window.screen.scale, 3)
        XCTAssertEqual(window.bounds.size, CGSize(width: 402, height: 874))
        XCTAssertGreaterThan(window.safeAreaInsets.top, 0)
        XCTAssertGreaterThan(window.safeAreaInsets.bottom, 0)
        XCTAssertEqual(scene.activationState, .foregroundActive)
        XCTAssertTrue(window.isKeyWindow)
        Self.captureSequence += 1
        let previousStyle = window.overrideUserInterfaceStyle
        let previousRoot = window.rootViewController
        defer {
            window.rootViewController = previousRoot
            window.overrideUserInterfaceStyle = previousStyle
        }
        window.overrideUserInterfaceStyle = scheme == .dark ? .dark : .light
        let view = ExampleCollectionView(initialState: state)
            .environment(\.locale, Locale(identifier: "en_US"))
            .environment(\.timeZone, TimeZone(secondsFromGMT: 0) ?? .current)
            .environment(\.sizeCategory, ContentSizeCategory.medium)
            .preferredColorScheme(scheme)
        let host = UIHostingController(rootView: view)
        host.overrideUserInterfaceStyle = scheme == .dark ? .dark : .light
        XCTAssertEqual(window.traitCollection.userInterfaceStyle, host.traitCollection.userInterfaceStyle)
        let strategy = imageStrategy(window: window, scheme: scheme)
        let started = ProcessInfo.processInfo.systemUptime
        let captured = expectation(description: "Captured \(name) in the app window")
        var image: UIImage?
        strategy.snapshot(host).run { result in
            image = result
            captured.fulfill()
        }
        wait(for: [captured], timeout: 30)
        let context = captureContext(
            window: window, host: host,
            scheme: scheme, previousStyle: previousStyle, previousRoot: previousRoot
        )
        saveCapture(image, name: name, started: started, context: context)
    }

    private func imageStrategy(window: UIWindow, scheme: ColorScheme) -> Snapshotting<UIViewController, UIImage> {
        let traits = UITraitCollection(mutations: { traits in
            traits.displayScale = 3
            traits.userInterfaceStyle = scheme == .dark ? .dark : .light
        })
        let configuration = ViewImageConfig(safeArea: window.safeAreaInsets, size: window.bounds.size, traits: traits)
        return Snapshotting<UIViewController, UIImage>.image(
            on: configuration, drawHierarchyInKeyWindow: true,
            precision: 1, perceptualPrecision: 1, traits: traits
        )
    }

    private func captureContext(
        window: UIWindow, host: UIViewController,
        scheme: ColorScheme, previousStyle: UIUserInterfaceStyle, previousRoot: UIViewController?
    ) -> [String: Any] {
        let insets = window.safeAreaInsets
        return [
            "sequence": Self.captureSequence,
            "requestedAppearance": scheme == .dark ? "dark" : "light",
            "previousWindowStyle": previousStyle.rawValue,
            "previousRootPresent": previousRoot != nil,
            "rootPresentAfterCapture": window.rootViewController != nil,
            "windowStyleAtCapture": window.overrideUserInterfaceStyle.rawValue,
            "windowTraitAtCapture": window.traitCollection.userInterfaceStyle.rawValue,
            "hostTraitAtCapture": host.traitCollection.userInterfaceStyle.rawValue,
            "sceneActivationState": window.windowScene?.activationState.rawValue ?? -1,
            "isKeyWindow": window.isKeyWindow,
            "scale": window.screen.scale,
            "size": ["width": window.bounds.width, "height": window.bounds.height],
            "safeArea": ["top": insets.top, "left": insets.left, "bottom": insets.bottom, "right": insets.right],
        ]
    }

    private func saveCapture(_ image: UIImage?, name: String, started: TimeInterval, context: [String: Any]) {
        guard let data = image?.pngData() else {
            XCTFail("Could not encode rendered image for \(name)")
            return
        }
        let root = URL(fileURLWithPath: #filePath)
            .deletingLastPathComponent().deletingLastPathComponent()
            .deletingLastPathComponent().deletingLastPathComponent()
        let rendered = root.appendingPathComponent("TestResults/Rendered")
        do {
            try FileManager.default.createDirectory(at: rendered, withIntermediateDirectories: true)
            try data.write(to: rendered.appendingPathComponent("components.\(name).png"), options: .atomic)
            let seconds = ProcessInfo.processInfo.systemUptime - started
            try String(seconds).write(
                to: rendered.appendingPathComponent("components.\(name).seconds"),
                atomically: true, encoding: .utf8
            )
            let details = try JSONSerialization.data(withJSONObject: context, options: [.prettyPrinted, .sortedKeys])
            try details.write(to: rendered.appendingPathComponent("components.\(name).context.json"), options: .atomic)
        } catch {
            XCTFail("Could not save rendered image for \(name): \(error)")
        }
    }
}
