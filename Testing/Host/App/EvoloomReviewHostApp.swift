import EvoloomReviewFixtures
import SwiftUI

@main
struct EvoloomReviewHostApp: App {
    private let arguments = ProcessInfo.processInfo.arguments

    private var scheme: ColorScheme {
        arguments.contains("--dark") ? .dark : .light
    }

    private var screen: ReviewFixtureScreen {
        let value = arguments.first(where: { $0.hasPrefix("--screen=") })?.replacingOccurrences(of: "--screen=", with: "")
        return ReviewFixtureScreen(rawValue: value ?? "") ?? .collection
    }

    private var state: CollectionState {
        let value = arguments.first(where: { $0.hasPrefix("--state=") })?.replacingOccurrences(of: "--state=", with: "")
        return CollectionState(rawValue: value ?? "") ?? .normal
    }

    var body: some Scene {
        WindowGroup {
            ReviewFixtureView(screen: screen, collectionState: state)
                .preferredColorScheme(scheme)
        }
    }
}
