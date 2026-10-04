import SwiftUI

/// Development-only routes for the host app; this target is outside the Evoloom product.
public enum ReviewFixtureScreen: String {
    case collection, controls, feedback, settings, settingsError, settingsJapanese, settingsJapaneseError, detail
}

public struct ReviewFixtureView: View {
    private let screen: ReviewFixtureScreen
    private let collectionState: CollectionState

    public init(screen: ReviewFixtureScreen = .collection, collectionState: CollectionState = .normal) {
        self.screen = screen
        self.collectionState = collectionState
    }

    public var body: some View {
        switch screen {
        case .collection:
            ExampleCollectionView(initialState: collectionState)
        case .controls:
            ReviewComponentsView(page: .controls)
        case .feedback:
            ReviewComponentsView(page: .feedback)
        case .settings:
            ReviewSettingsView()
        case .settingsError:
            ReviewSettingsView(showError: true)
        case .settingsJapanese:
            ReviewSettingsView(longJapanese: true)
                .environment(\.locale, Locale(identifier: "ja_JP"))
        case .settingsJapaneseError:
            ReviewSettingsView(showError: true, longJapanese: true)
                .environment(\.locale, Locale(identifier: "ja_JP"))
        case .detail:
            ReviewDetailView()
        }
    }
}
