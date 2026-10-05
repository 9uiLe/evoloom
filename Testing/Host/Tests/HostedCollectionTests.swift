import EvoloomReviewFixtures
import SnapshotTesting
import SwiftUI
import UIKit
import XCTest

@MainActor
final class HostedCollectionTests: XCTestCase {
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
        window.overrideUserInterfaceStyle = scheme == .dark ? .dark : .light
        let view = ExampleCollectionView(initialState: state)
            .environment(\.locale, Locale(identifier: "en_US"))
            .environment(\.timeZone, TimeZone(secondsFromGMT: 0) ?? .current)
            .environment(\.sizeCategory, ContentSizeCategory.medium)
            .preferredColorScheme(scheme)
        let host = UIHostingController(rootView: view)
        host.overrideUserInterfaceStyle = scheme == .dark ? .dark : .light
        let traits = UITraitCollection(mutations: { traits in
            traits.displayScale = 3
            traits.userInterfaceStyle = scheme == .dark ? .dark : .light
        })
        let configuration = ViewImageConfig(
            safeArea: window.safeAreaInsets,
            size: window.bounds.size,
            traits: traits
        )
        let strategy = Snapshotting<UIViewController, UIImage>.image(
            on: configuration,
            drawHierarchyInKeyWindow: true,
            precision: 1,
            perceptualPrecision: 1,
            traits: traits
        )
        let started = ProcessInfo.processInfo.systemUptime
        let captured = expectation(description: "Captured \(name) in the app window")
        var image: UIImage?
        strategy.snapshot(host).run { result in
            image = result
            captured.fulfill()
        }
        wait(for: [captured], timeout: 30)
        saveCapture(image, name: name, started: started)
    }

    private func saveCapture(_ image: UIImage?, name: String, started: TimeInterval) {
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
        } catch {
            XCTFail("Could not save rendered image for \(name): \(error)")
        }
    }
}
