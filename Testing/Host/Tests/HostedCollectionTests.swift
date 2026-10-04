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
        var strategy = Snapshotting<UIViewController, UIImage>.image(
            on: configuration,
            drawHierarchyInKeyWindow: true,
            precision: 1,
            perceptualPrecision: 1,
            traits: traits
        )
        let root = URL(fileURLWithPath: #filePath)
            .deletingLastPathComponent().deletingLastPathComponent()
            .deletingLastPathComponent().deletingLastPathComponent()
        strategy.diffing = exactImageDiffing(strategy.diffing, root: root, name: name)
        let isRecording = FileManager.default.fileExists(atPath: root.appendingPathComponent(".prepared/record-host-snapshots").path)
        if isRecording {
            let message = verifySnapshot(of: host, as: strategy, named: name, record: true, testName: "components")
            XCTAssertTrue(message?.contains("Record mode is on.") == true, message ?? "Snapshot recording failed")
        } else {
            assertSnapshot(of: host, as: strategy, named: name, record: false, testName: "components")
        }
    }
}
